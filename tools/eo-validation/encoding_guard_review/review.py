import importlib.util, json, shutil, hashlib, sys, argparse, tempfile
from pathlib import Path
import numpy as np
parser=argparse.ArgumentParser(description='Independent offline adversarial checks; writes only temporary fixtures and the selected output receipt.')
parser.add_argument('--evidence-root',type=Path,required=True)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--run-id',required=True)
args=parser.parse_args()
workspace=tempfile.TemporaryDirectory(prefix='sahool-guard-review-',dir=str(args.output.resolve().parent))
ROOT=Path(workspace.name)
SRC=args.evidence_root/'encoding_guard'/'guard.py'
guard_hash_before=hashlib.sha256(SRC.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('guard',SRC);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
BASE=args.evidence_root/'yemen_march_selected'
sample_names=['yemen','yemen_march_selected','yemen_december_fixed_window']
input_hashes_before={str(p.relative_to(args.evidence_root)):hashlib.sha256(p.read_bytes()).hexdigest() for n in sample_names for p in (args.evidence_root/n).iterdir() if p.is_file()}
results=[]
def case(name, mutate, reject=True, check=None):
 p=ROOT/name
 if p.exists():shutil.rmtree(p)
 shutil.copytree(BASE,p)
 mutate(p)
 try:
  r=g.compare(p)
  # enforce public serialized output contract
  json.dumps(r,allow_nan=False)
  ok=not reject and (check(r) if check else True)
  results.append({'case':name,'passed':bool(ok),'outcome':'returned','detail':None if ok else r})
 except Exception as e:
  ok=reject and isinstance(e,(g.Rejected,KeyError,ValueError,IndexError,OSError))
  results.append({'case':name,'passed':ok,'outcome':type(e).__name__,'detail':str(e)})
def mutate_json(p,n,f):
 q=p/n;v=json.loads(q.read_text());f(v);q.write_text(json.dumps(v))
def product(p):mutate_json(p,'c1_item.json',lambda d:d['properties'].__setitem__('s2:product_uri','different'))
def grid(p):mutate_json(p,'window_metadata.json',lambda d:d['c1_nir']['transform'].__setitem__(2,d['c1_nir']['transform'][2]+10))
def missing_offset(p):mutate_json(p,'old_item.json',lambda d:d['assets']['red']['raster:bands'][0].pop('offset'))
def unknownflag(p):mutate_json(p,'old_item.json',lambda d:d['properties'].pop('earthsearch:boa_offset_applied'))
def allinvalid(p):
 for k in ['old_red','old_nir','c1_red','c1_nir']:
  with np.load(p/(k+'.npz')) as z:a=z['data'];m=np.ones(a.shape,bool)
  np.savez_compressed(p/(k+'.npz'),data=a,mask=m)
def zeros(p):
 for k in ['old_red','old_nir','c1_red','c1_nir']:
  with np.load(p/(k+'.npz')) as z:a=np.zeros_like(z['data']);m=np.zeros(a.shape,bool)
  np.savez_compressed(p/(k+'.npz'),data=a,mask=m)
def shape(p):
 with np.load(p/'old_nir.npz') as z:a=z['data'][:1];m=z['mask'][:1]
 np.savez_compressed(p/'old_nir.npz',data=a,mask=m)
def scl_shift(p):
 with np.load(p/'c1_scl.npz') as z:a=z['aligned'].copy();s=z['source']
 a=np.roll(a,3,axis=0)
 np.savez_compressed(p/'c1_scl.npz',aligned=a,source=s)
def sourceurl(p):mutate_json(p,'window_metadata.json',lambda d:d['old_scl'].__setitem__('url','https://other.example/SCL.tif'))
case('scl_asset_transform_mismatch',lambda p:mutate_json(p,'c1_item.json',lambda d:d['assets']['scl']['proj:transform'].__setitem__(2,d['assets']['scl']['proj:transform'][2]+20)))
case('scl_source_window_mismatch',lambda p:mutate_json(p,'window_metadata.json',lambda d:d['c1_scl']['source_window'].__setitem__(0,d['c1_scl']['source_window'][0]+1)))
def put_pixel(p,k,value):
 with np.load(p/(k+'.npz')) as z:a=z['data'].astype(float);m=z['mask']
 a[0,0]=value
 np.savez_compressed(p/(k+'.npz'),data=a,mask=m)
case('nonfinite_raw',lambda p:put_pixel(p,'old_red',float('nan')),False,lambda r:r['common_raw_valid_pixels']==65535 and r['quality_flag_counts_overlapping']['old_declared']['nonfinite_reflectance']==1)
def zero_denominator(p):
 for k in ['old','c1']:
  put_pixel(p,k+'_red',1500);put_pixel(p,k+'_nir',500)
case('zero_denominator',zero_denominator,False,lambda r:r['common_numeric_pixels']==65535 and r['numeric_exclusions_after_raw_mask']==1 and r['quality_flag_counts_overlapping']['c1_declared']['near_zero_denominator_numerical_only']==1)
case('product_mismatch',product)
case('grid_mismatch',grid)
case('missing_offset',missing_offset)
case('shape_mismatch',shape)
case('unknown_flag',unknownflag,False,lambda r:r['old_boa_offset_applied'] is None and r['flag_assessment']=='unknown_flag_no_encoding_inference')
case('all_invalid',allinvalid,False,lambda r:r['common_numeric_pixels']==0 and all(x is None for x in r['comparisons'].values()))
case('nodata_zero_without_mask',zeros,False,lambda r:r['common_raw_valid_pixels']==0 and r['common_numeric_pixels']==0)
case('scl_shift',scl_shift)
case('scl_url_mismatch',sourceurl)
red=np.array([[-.2,.1,0.,np.nan,.1]]);nir=np.array([[.4,-.1,0.,.2,.2]])
a,f=g.quality(red,nir,np.array([[False,False,False,False,True]]),np.array([[4,8,3,13,0]]))
results.append({'case':'quality_flags_no_clamp','passed':bool(a[0,0]>1 and f['negative_reflectance'][0,0] and np.isnan(a[0,1]) and f['near_zero_denominator_numerical_only'][0,1] and f['scl_cloud'][0,1] and f['scl_shadow'][0,2] and f['nonfinite_reflectance'][0,3] and f['scl_invalid_label'][0,3] and f['nodata'][0,4])})
for dirname,red_residual,nveg in [('yemen',0,62),('yemen_march_selected',7,448),('yemen_december_fixed_window',0,12520)]:
 r=g.compare(BASE.parent/dirname)
 results.append({'case':'real_'+dirname,'passed':r['band_residuals']['red']['scale_only_residual_pixels']==red_residual and r['band_residuals']['nir']['scale_only_residual_pixels']==0 and r['scl_vegetation_pixels']['old']==nveg and len(r['input_sha256'])==9 and r['automatic_correction_authorized'] is False})
input_hashes_after={str(p.relative_to(args.evidence_root)):hashlib.sha256(p.read_bytes()).hexdigest() for n in sample_names for p in (args.evidence_root/n).iterdir() if p.is_file()}
results.append({'case':'source_and_inputs_unchanged','passed':input_hashes_before==input_hashes_after and guard_hash_before==hashlib.sha256(SRC.read_bytes()).hexdigest()})
result={'schema':'eo-independent-v1','run_id':args.run_id,'input_sha256':input_hashes_before,'source_inputs_unchanged':input_hashes_before==input_hashes_after and guard_hash_before==hashlib.sha256(SRC.read_bytes()).hexdigest(),'guard_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'cases':results,'all_passed':all(x['passed'] for x in results)}
args.output.write_text(json.dumps(result,indent=2));print(json.dumps({'all_passed':result['all_passed'],'cases':[{k:v for k,v in r.items() if k!='detail'} for r in results]},indent=2))

workspace.cleanup()

raise SystemExit(0 if result["all_passed"] else 1)
