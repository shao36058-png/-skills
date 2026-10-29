#!/usr/bin/env python3
"""Audit complete complex modal S data offline; requires NumPy, never calls AEDT."""
import argparse
import json
from pathlib import Path
import numpy as np


def load_network(raw):
    channels=raw['channel_order']
    if len(channels)<3 or len(channels)!=len(set(channels)):raise ValueError('At least three unique modal channels required')
    freq=np.asarray(raw['frequencies_GHz'],float)
    if freq.ndim!=1 or len(freq)<2 or not np.isfinite(freq).all() or not (np.diff(freq)>0).all():
        raise ValueError('Frequency grid must be finite and strictly increasing')
    def values(expression):
        d=raw['data'][expression]
        z=np.asarray(d['real'],float)+1j*np.asarray(d['imag'],float)
        if z.shape!=freq.shape or not np.isfinite(z).all():raise ValueError('Invalid '+expression)
        return z
    s=np.array([[values(f'S({i},{j})') for j in channels] for i in channels]).transpose(2,0,1)
    return freq,channels,s


def db(z):return 20*np.log10(np.maximum(abs(z),1e-30))


def powers(s,a,output,inputs,loads):
    pin=float(np.vdot(a,a).real)
    if pin<=0:raise ValueError('Positive incident power required')
    p=abs(s@a)**2;loss=pin-p.sum(axis=1)
    return dict(incident_W=pin,source_power_W=(abs(a)**2).tolist(),
        power_by_channel_W=p.tolist(),efficiency_pct=(100*p[:,output]/pin).tolist(),
        efficiency_min_pct=float(100*p[:,output].min()/pin),efficiency_max_pct=float(100*p[:,output].max()/pin),
        returned_to_inputs_max_W=float(p[:,inputs].sum(axis=1).max()),
        load_channels_max_W=float(p[:,loads].sum(axis=1).max()) if loads else 0.,
        loss_and_numerical_residual_W=loss.tolist(),
        loss_and_residual_range_W=[float(loss.min()),float(loss.max())])


def terminated(s,load_ids,gamma):
    """Eliminate matched/reﬂecting load modes using b=S a and a_L=Gamma b_L."""
    keep=[i for i in range(s.shape[1]) if i not in load_ids]
    skk=s[:,keep,:][:,:,keep];skl=s[:,keep,:][:,:,load_ids]
    slk=s[:,load_ids,:][:,:,keep];sll=s[:,load_ids,:][:,:,load_ids]
    g=np.diag(np.broadcast_to(np.asarray(gamma,dtype=complex),len(load_ids)))
    return keep,skk+skl@np.linalg.solve(np.eye(len(load_ids))[None,:,:]-g@sll,g@slk)


def audit(raw,load_return_losses=()):
    freq,ch,s=load_network(raw);cfg=raw['audit_config']
    input_channels=cfg['input_channels'];inputs=[ch.index(c) for c in input_channels]
    if len(inputs)!=2 or len(set(inputs))!=2:raise ValueError('Two distinct input modes required')
    out=ch.index(cfg['output_channel']);loads=[ch.index(c) for c in cfg.get('load_channels',[])]
    if len(loads)!=len(set(loads)) or out in inputs or set(loads)&(set(inputs)|{out}):
        raise ValueError('Duplicate or overlapping channel roles')
    src=np.zeros(len(ch),complex)
    for c,p,ph in zip(input_channels,cfg.get('powers_W',[.5,.5]),cfg.get('phases_deg',[0,0]),strict=True):
        if not np.isfinite([p,ph]).all() or p<=0:raise ValueError('Each input needs finite positive power and finite phase')
        src[ch.index(c)]=np.sqrt(p)*np.exp(1j*np.deg2rad(ph))
    cases={'balanced':powers(s,src,out,inputs,loads)}
    for i in range(2):
        a=np.zeros_like(src);a[inputs[i]]=src[inputs[i]]
        cases[f'only_input{i+1}']=powers(s,a,out,inputs,loads)
    a=src.copy();a[inputs[1]]*=-1;cases['antiphase']=powers(s,a,out,inputs,loads)
    for phase in [-20,-10,10,20]:
        a=src.copy();a[inputs[1]]*=np.exp(1j*np.deg2rad(phase))
        cases[f'phase_error_{phase:+d}deg']=powers(s,a,out,inputs,loads)
    for err in [-1,1]:
        total=float(np.vdot(src,src).real);ratio=10**(err/10)
        a=src.copy();a[inputs[0]]=np.sqrt(total/(1+ratio))*np.exp(1j*np.angle(src[inputs[0]]))
        a[inputs[1]]=np.sqrt(total*ratio/(1+ratio))*np.exp(1j*np.angle(src[inputs[1]]))
        cases[f'input2_power_error_{err:+d}dB']=powers(s,a,out,inputs,loads)
    reciprocal=float(abs(s-s.transpose(0,2,1)).max())
    max_sv=float(np.linalg.svd(s,compute_uv=False).max())
    iso=-db(s[:,inputs[1],inputs[0]])
    valid=(abs(s[:,out,inputs[0]])>1e-30)&(abs(s[:,out,inputs[1]])>1e-30)
    path=s[valid,out,inputs[0]]/s[valid,out,inputs[1]]
    phase=np.full(len(freq),np.nan);amplitude=phase.copy()
    phase[valid]=np.angle(path,deg=True);amplitude[valid]=db(path)
    nullable=lambda x:[float(v) if np.isfinite(v) else None for v in x]
    result=dict(case_id=raw.get('case_id'),frequency_GHz=[float(freq[0]),float(freq[-1])],points=len(freq),
        channel_order=ch,cases=cases,input_isolation_min_dB=float(iso.min()),input_isolation_dB=iso.tolist(),
        self_reflection_worst_dB={c:float(db(s[:,i,i]).max()) for i,c in enumerate(ch)},
        path_phase_difference_deg=nullable(phase),
        path_amplitude_difference_dB=nullable(amplitude),
        reciprocity_max_error=reciprocal,maximum_singular_value=max_sv,
        interpretation='Modal power-wave normalization; all listed channels are propagating. Residual includes numerical error.',
        source_evidence=raw.get('evidence',{}))
    if reciprocal>1e-5 or max_sv>1.005:raise ValueError('Reciprocity/passivity check failed')
    if min(v['loss_and_residual_range_W'][0] for v in cases.values())<-.005:
        raise ValueError('Power conservation check failed')
    if loads and load_return_losses:
        study={}
        for rl in load_return_losses:
            if not np.isfinite(rl) or rl<=0:raise ValueError('Load return loss must be finite and positive')
            worst_iso=1e9;worst_eta=1e9
            # For multiple loads this is a common-phase scan, NOT independent-phase worst case.
            for phase in range(0,360,2):
                keep,se=terminated(s,loads,10**(-rl/20)*np.exp(1j*np.deg2rad(phase)))
                i,j,o=[keep.index(k) for k in [*inputs,out]]
                worst_iso=min(worst_iso,float((-db(se[:,j,i])).min()))
                b=se@src[keep];eta=100*abs(b[:,o])**2/float(np.vdot(src,src).real)
                worst_eta=min(worst_eta,float(eta.min()))
            study[str(rl)]=dict(return_loss_dB=rl,input_isolation_worst_dB=worst_iso,
                efficiency_worst_pct=worst_eta,phase_step_deg=2,
                scope='Single-load full phase scan' if len(loads)==1 else 'All loads share phase; not independent worst case')
        result['load_reflection_study']=study
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True,type=Path);ap.add_argument('--output',type=Path)
    ap.add_argument('--min-efficiency-pct',type=float);ap.add_argument('--min-isolation-db',type=float)
    ap.add_argument('--load-return-loss-db',type=float,action='append',default=[])
    args=ap.parse_args()
    raw=json.loads(args.input.read_text(encoding='utf-8'));result=audit(raw,args.load_return_loss_db)
    text=json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)
    if args.output:args.output.write_text(text+'\n',encoding='utf-8')
    else:print(text)
    errors=[]
    if args.min_efficiency_pct is not None and result['cases']['balanced']['efficiency_min_pct']<args.min_efficiency_pct:
        errors.append('Combining efficiency below threshold')
    if args.min_isolation_db is not None and result['input_isolation_min_dB']<args.min_isolation_db:
        errors.append('Independent input isolation below threshold')
    if errors:raise SystemExit('; '.join(errors))


if __name__=='__main__':main()
