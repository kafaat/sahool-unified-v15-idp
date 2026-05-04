import { useState, useRef, useEffect, useCallback } from "react";

/* ═══════════════════════════════════════════════════════════════
  DATA
═══════════════════════════════════════════════════════════════ */
const FIELDS = [
  {id:1,n:"حقل الشمال",    crop:"قمح",   area:"2.4", ndvi:.78, ec:1.1, moist:52, elev:820, st:"g", dir:[], lat:24.5, lng:46.7, boundary:[[24.51,46.68],[24.51,46.72],[24.49,46.72],[24.49,46.68]]},
  {id:2,n:"الوادي الأوسط", crop:"ذرة",   area:"1.8", ndvi:.61, ec:1.8, moist:38, elev:760, st:"a", dir:["NW","SW"], lat:24.48, lng:46.72, boundary:[[24.49,46.70],[24.49,46.74],[24.47,46.74],[24.47,46.70]]},
  {id:3,n:"المدرج الجنوبي",crop:"بن",    area:"3.1", ndvi:.85, ec:.9,  moist:68, elev:1180,st:"g", dir:[], lat:24.45, lng:46.68, boundary:[[24.46,46.66],[24.46,46.70],[24.44,46.70],[24.44,46.66]]},
  {id:4,n:"حوض الغرب",     crop:"طماطم", area:"0.9", ndvi:.44, ec:2.4, moist:28, elev:690, st:"r", dir:["W","SW"], lat:24.52, lng:46.65, boundary:[[24.525,46.63],[24.525,46.67],[24.515,46.67],[24.515,46.63]]},
  {id:5,n:"المزرعة الشرقية",crop:"أرز",  area:"4.2", ndvi:.72, ec:1.3, moist:55, elev:840, st:"g", dir:["E"], lat:24.55, lng:46.78, boundary:[[24.56,46.76],[24.56,46.80],[24.54,46.80],[24.54,46.76]]},
];

const ALL_INDICES = [
  {id:"hybrid",  lab:"Hybrid",  cat:"أساسي",       c:"#10B981", desc:"يجمع NDVI+NDWI في صورة واحدة — 5 ألوان للمزارع البسيط"},
  {id:"ndvi",    lab:"NDVI",    cat:"صحة مبكرة",   c:"#22C55E", desc:"الصحة الخضرية العامة — المرحلة المبكرة من النمو"},
  {id:"evi",     lab:"EVI",     cat:"صحة مبكرة",   c:"#4ADE80", desc:"تصحيح جوي وتربة — أفضل من NDVI عند الكثافة العالية"},
  {id:"savi",    lab:"SAVI",    cat:"صحة مبكرة",   c:"#86EFAC", desc:"تصحيح تأثير التربة — مناسب للأراضي الجافة والقاحلة"},
  {id:"ndre",    lab:"NDRE",    cat:"صحة متأخرة",  c:"#A3E635", desc:"للكثافة العالية: ذرة، فول صويا، بن — المرحلة المتأخرة"},
  {id:"ndwi",    lab:"NDWI",    cat:"ري",           c:"#38BDF8", desc:"نقص الماء في الأوراق والأنسجة النباتية"},
  {id:"et",      lab:"ET",      cat:"ري",           c:"#7DD3FC", desc:"التبخر النتحي — معدل فقد الماء من التربة والنبات"},
  {id:"ndmi",    lab:"NDMI",    cat:"ري",           c:"#BAE6FD", desc:"رطوبة التربة المشتقة من الأقمار الصناعية"},
  {id:"soc",     lab:"SOC",     cat:"تربة",         c:"#D97706", desc:"الكربون العضوي — مؤشر خصوبة التربة قبل الزراعة"},
  {id:"erosion", lab:"Erosion", cat:"تربة",         c:"#EF4444", desc:"تآكل التربة وانجرافها"},
  {id:"dem",     lab:"DEM",     cat:"تضاريس",       c:"#8B5CF6", desc:"نموذج الارتفاع الرقمي — مناطق تجمع المياه والصرف"},
  {id:"rvi",     lab:"RVI",     cat:"SAR رادار",    c:"#F59E0B", desc:"صحة المحصول بالرادار — يخترق الغيوم تلقائياً"},
  {id:"rsm",     lab:"RSM",     cat:"SAR رادار",    c:"#FCD34D", desc:"رطوبة التربة بالرادار — عند الغيوم الكثيفة"},
  {id:"tci",     lab:"TCI",     cat:"صورة",         c:"#0EA5E9", desc:"صورة قمرية طبيعية الألوان"},
  {id:"etci",    lab:"ETCI",    cat:"صورة",         c:"#38BDF8", desc:"صورة محسّنة لإبراز تفاصيل الغطاء النباتي"},
  {id:"cb",      lab:"CB",      cat:"وصول",         c:"#94A3B8", desc:"نمط لعمى الألوان — إمكانية الوصول الشاملة"},
];

const HYBRID_SCALE = [
  {c:"#10B981", label:"صحة المحصول والري ممتازان",               en:"Good Crop Health & Irrigation"},
  {c:"#F97316", label:"صحة المحصول تحتاج انتباهاً",              en:"Requires Crop Health Attention"},
  {c:"#8B5CF6", label:"الري يحتاج انتباهاً",                     en:"Requires Irrigation Attention"},
  {c:"#EF4444", label:"كلاهما حرج أو لا محصول",                  en:"Both Critical / No Crop"},
  {c:"#CBD5E1", label:"غيوم تغطي الحقل — بيانات SAR متاحة",      en:"Clouds — SAR fallback active"},
];

const DIR_CELLS = [
  {id:"NW",ar:"ش·غ"},{id:"N",ar:"شمال"},{id:"NE",ar:"ش·ش"},
  {id:"W", ar:"غرب"},{id:"C",ar:"وسط"}, {id:"E", ar:"شرق"},
  {id:"SW",ar:"ج·غ"},{id:"S",ar:"جنوب"},{id:"SE",ar:"ج·ش"},
];

const WX7 = [
  {d:"السبت",   ic:"☀",  hi:28,lo:16,prob:5},
  {d:"الأحد",   ic:"⛅", hi:26,lo:14,prob:22},
  {d:"الاثنين", ic:"🌧", hi:22,lo:12,prob:75},
  {d:"الثلاثاء",ic:"⛅", hi:24,lo:13,prob:30},
  {d:"الأربعاء",ic:"☀",  hi:27,lo:15,prob:8},
  {d:"الخميس",  ic:"☀",  hi:29,lo:17,prob:3},
  {d:"الجمعة",  ic:"☀",  hi:30,lo:18,prob:2},
];

const SENSORS = [
  {id:"S-001",n:"رطوبة التربة A",  field:"حقل الشمال",    v:52,  u:"%",    opt:[35,65],mx:100,dep:"20سم",bat:87,sig:4,last:"3 د"},
  {id:"S-002",n:"رطوبة التربة B",  field:"الوادي الأوسط", v:38,  u:"%",    opt:[35,65],mx:100,dep:"20سم",bat:92,sig:4,last:"2 د"},
  {id:"S-003",n:"EC الملوحة A",    field:"حوض الغرب",     v:2.4, u:"dS/m", opt:[.5,2], mx:5,  dep:"30سم",bat:61,sig:3,last:"5 د"},
  {id:"S-004",n:"درجة الحرارة",    field:"المدرج الجنوبي",v:24,  u:"°م",   opt:[15,35],mx:50, dep:"هواء",bat:78,sig:5,last:"1 د"},
  {id:"S-005",n:"رطوبة الهواء",    field:"حقل الشمال",    v:65,  u:"%",    opt:[40,80],mx:100,dep:"هواء",bat:95,sig:5,last:"1 د"},
  {id:"S-006",n:"EC الملوحة B",    field:"الوادي الأوسط", v:1.8, u:"dS/m", opt:[.5,2], mx:5,  dep:"30سم",bat:43,sig:2,last:"8 د"},
  {id:"S-007",n:"pH التربة",       field:"المدرج الجنوبي",v:6.3, u:"pH",   opt:[5.5,7],mx:14, dep:"10سم",bat:71,sig:4,last:"4 د"},
];

const TASKS = [
  {id:1,t:"ري الوادي الأوسط",     f:"الوادي الأوسط",  tm:"08:00",   p:"h",done:false,a:"علي",    due:"اليوم"},
  {id:2,t:"فحص مستشعر EC #1",    f:"حوض الغرب",      tm:"10:30",   p:"h",done:false,a:"أحمد",   due:"اليوم"},
  {id:3,t:"رش وقائي من آفات",    f:"حقل الشمال",     tm:"14:00",   p:"m",done:true, a:"محمد",   due:"اليوم"},
  {id:4,t:"تسجيل بيانات الغلة",  f:"المدرج الجنوبي", tm:"16:00",   p:"l",done:false,a:"علي",    due:"اليوم"},
  {id:5,t:"إضافة سماد نيتروجيني",f:"الوادي الأوسط",  tm:"غداً 7:00",p:"h",done:false,a:"أحمد",  due:"غداً"},
  {id:6,t:"فحص صحة نباتات البن", f:"المدرج الجنوبي", tm:"غداً 9:00",p:"m",done:false,a:"فاطمة", due:"غداً"},
  {id:7,t:"تحديث بيانات الطقس",  f:"الكل",           tm:"يومياً",  p:"l",done:false,a:"النظام", due:"دوري"},
];

const TEAM = [
  {id:1,n:"أحمد المزارع",    role:"admin",  fields:4,join:"8 أشهر",st:"on",  av:"أ",email:"ahmed@sahool.ye"},
  {id:2,n:"علي الزراعي",     role:"editor", fields:3,join:"3 أشهر",st:"on",  av:"ع",email:"ali@sahool.ye"},
  {id:3,n:"محمد التقني",     role:"viewer", fields:2,join:"شهر",    st:"off", av:"م",email:"m.tech@sahool.ye"},
  {id:4,n:"فاطمة المستشارة", role:"editor", fields:4,join:"أسبوع",  st:"on",  av:"ف",email:"fatima@sahool.ye"},
];

const MACHINES = [
  {id:"M-001",n:"S690 Combine",   type:"حصاد",  fuel:42,def:8, hours:1247,loc:"حقل الشمال",    st:"on", next:"صيانة 1500",alert:null},
  {id:"M-002",n:"8R 410 Tractor", type:"جرار",  fuel:68,def:45,hours:892, loc:"الوادي الأوسط", st:"on", next:"",alert:"حرارة مبرد عالية"},
  {id:"M-003",n:"Sprayer 4730",   type:"رش",    fuel:55,def:32,hours:456, loc:"حوض الغرب",     st:"off",next:"غداً",alert:null},
  {id:"M-004",n:"Planter 1775",   type:"زراعة", fuel:78,def:67,hours:234, loc:"المدرج الجنوبي",st:"on", next:"جاهز",alert:null},
];

const SCOUT_NOTES = [
  {id:1,field:"الوادي الأوسط",date:"2026-05-03",author:"علي",   type:"تحذير",  note:"بقع صفراء على أطراف أوراق الذرة في الزاوية الشمالية الغربية",img:true},
  {id:2,field:"حقل الشمال",   date:"2026-05-02",author:"أحمد",  type:"معلومة", note:"ظهور جيد للسنابل، رطوبة مثالية",img:true},
  {id:3,field:"حوض الغرب",    date:"2026-05-01",author:"فاطمة", type:"تحذير",  note:"EC مرتفع جداً في الجزء الغربي — يحتاج تصريف",img:false},
  {id:4,field:"المدرج الجنوبي",date:"2026-04-30",author:"محمد",  type:"جيد",    note:"نمو منتظم، لا آفات ظاهرة",img:true},
];

const VRA_ZONES = [
  {id:1,field:"حقل الشمال",    zone:"منخفضة",area:"0.8",rate:"120",unit:"كغ/هـ",type:"سماد N",color:"#EF4444"},
  {id:2,field:"حقل الشمال",    zone:"متوسطة",area:"1.2",rate:"100",unit:"كغ/هـ",type:"سماد N",color:"#F59E0B"},
  {id:3,field:"حقل الشمال",    zone:"عالية", area:"0.4",rate:"80", unit:"كغ/هـ",type:"سماد N",color:"#10B981"},
  {id:4,field:"الوادي الأوسط", zone:"منخفضة",area:"0.6",rate:"150",unit:"كغ/هـ",type:"سماد N",color:"#EF4444"},
  {id:5,field:"الوادي الأوسط", zone:"متوسطة",area:"0.9",rate:"130",unit:"كغ/هـ",type:"سماد N",color:"#F59E0B"},
  {id:6,field:"الوادي الأوسط", zone:"عالية", area:"0.3",rate:"100",unit:"كغ/هـ",type:"سماد N",color:"#10B981"},
];

const REPORT_DATES = [
  "25-03-2026","20-03-2026","15-03-2026","10-03-2026","05-03-2026",
  "28-02-2026","23-02-2026","18-02-2026","13-02-2026","08-02-2026",
];

const SCREENS = [
  {id:"dash",    ic:"⊞",  label:"لوحة القيادة",       group:"رئيسي"},
  {id:"map",     ic:"◎",  label:"الخريطة التفاعلية",   group:"رئيسي"},
  {id:"idx",     ic:"◈",  label:"طبقات المؤشرات",      group:"رئيسي"},
  {id:"ts",      ic:"▦",  label:"السلاسل الزمنية",     group:"تحليل"},
  {id:"rep",     ic:"▤",  label:"التقارير",             group:"تحليل"},
  {id:"wx",      ic:"☁",  label:"الطقس والـ GDD",      group:"تحليل"},
  {id:"scout",   ic:"◉",  label:"المسح الميداني",      group:"عمليات"},
  {id:"sensor",  ic:"≋",  label:"المستشعرات IoT",      group:"عمليات"},
  {id:"vra",     ic:"◆",  label:"خرائط VRA",           group:"عمليات"},
  {id:"tasks",   ic:"◻",  label:"المهام",              group:"إدارة"},
  {id:"team",    ic:"◫",  label:"الفريق",              group:"إدارة"},
  {id:"machines",ic:"🚜", label:"المعدات",             group:"إدارة"},
  {id:"ai",      ic:"◇",  label:"المستشار AI",         group:"ذكاء"},
  {id:"trace",   ic:"⬡",  label:"تتبع المنتج",         group:"ذكاء"},
  {id:"draw",    ic:"✎",  label:"رسم الحقول",          group:"أدوات"},
  {id:"finance", ic:"💰", label:"التمويل والتأمين",     group:"أدوات"},
  {id:"carbon",  ic:"🌱", label:"الكربون",             group:"أدوات"},
];

const AI_MESSAGES = [
  {from:"ai", text:"مرحباً! أنا مستشار SAHOOL الذكي. كيف يمكنني مساعدتك اليوم؟"},
  {from:"user", text:"حقل الوادي الأوسط يعاني من جفاف"},
  {from:"ai", text:"أنصحك بـ:
1. تفعيل الري التنقيطي فوراً لمدة 3 ساعات
2. تقليل الري السطحي لتجنب التبخر
3. إضافة مبلّل تربة في الجزء الغربي

توقع استعادة الرطوبة المثالية خلال 48 ساعة."},
  {from:"user", text:"هل يوجد تنبيهات على مستشعر EC؟"},
  {from:"ai", text:"نعم، مستشعر S-003 في حوض الغرب يسجل EC 2.4 dS/m (أعلى من الحد الأمثل 2.0).

التوصية:
• تقليل الري المالح
• فحص انسداد قنوات الصرف
• مراجعة برنامج التسميد"},
];

const TRACE_STEPS = [
  {step:1,title:"الزراعة",date:"2026-01-15",status:"done",   loc:"حقل الشمال",actor:"أحمد",cert:"ISO 22000"},
  {step:2,title:"التسميد",date:"2026-02-01",status:"done",   loc:"حقل الشمال",actor:"علي",  cert:"Organic"},
  {step:3,title:"الري",   date:"2026-02-15",status:"done",   loc:"حقل الشمال",actor:"النظام",cert:"Water-Smart"},
  {step:4,title:"الحصاد", date:"2026-05-10",status:"pending",loc:"حقل الشمال",actor:"—",    cert:"—"},
  {step:5,title:"التخزين",date:"2026-05-12",status:"pending",loc:"صوامع الشرق",actor:"—",   cert:"—"},
  {step:6,title:"التوزيع",date:"2026-05-20",status:"pending",loc:"—",          actor:"—",   cert:"—"},
];

const FINANCE_DATA = [
  {id:1,title:"تأمين المحاصيل 2026",provider:"شركة الاتحاد للتأمين",premium:24000,coverage:500000,status:"نشط",due:"15-01-2027",type:"تأمين"},
  {id:2,title:"قرض تشغيلي موسمي",provider:"بنك أبوظبي الأول",amount:150000,rate:"4.5%",status:"معلق",due:"30-06-2026",type:"قرض"},
  {id:3,title:"تمويل معدات",provider:"الراجحي",amount:850000,rate:"3.9%",status:"نشط",due:"15-12-2028",type:"تمويل"},
  {id:4,title:"تأمين طيران بدون طيار",provider:"AXA Green",premium:8500,coverage:120000,status:"نشط",due:"01-03-2027",type:"تأمين"},
];

const CARBON_DATA = {
  totalSequestered: 142.5,
  target: 500,
  credits: 285,
  price: 45,
  history: [
    {month:"يناير",sequestered:22.1,emitted:18.5},
    {month:"فبراير",sequestered:24.3,emitted:19.2},
    {month:"مارس",sequestered:28.7,emitted:21.4},
    {month:"أبريل",sequestered:31.2,emitted:20.8},
    {month:"مايو",sequestered:36.2,emitted:22.1},
  ],
  practices: [
    {name:"تدوير المحاصيل",impact:45.2,status:"مطبق"},
    {name:"الزراعة التقليلية",impact:38.7,status:"مطبق"},
    {name:"الأسمدة العضوية",impact:28.4,status:"جزئي"},
    {name:"الري بالتنقيط",impact:30.2,status:"مطبق"},
  ]
};

/* ═══════════════════════════════════════════════════════════════
  TYPES
═══════════════════════════════════════════════════════════════ */
type ScreenId = "dash"|"map"|"idx"|"ts"|"rep"|"wx"|"scout"|"ai"|"sensor"|"tasks"|"team"|"vra"|"trace"|"machines"|"draw"|"finance"|"carbon";
interface Field {id:number;n:string;crop:string;area:string;ndvi:number;ec:number;moist:number;elev:number;st:string;dir:string[];lat:number;lng:number;boundary:number[][];}

/* ═══════════════════════════════════════════════════════════════
  JD DESIGN SYSTEM — inspired by John Deere Operations Center
═══════════════════════════════════════════════════════════════ */
const JD = {
  /* Brand */
  green:       "#367C2B",
  greenDark:   "#1e5218",
  greenLight:  "#3f9e30",
  greenGlow:   "#4caf50",
  yellow:      "#FFDE00",
  yellowDark:  "#e6c800",
  /* Surfaces — dark industrial */
  bg:          "#090e18",
  panel:       "#0d1520",
  surface:     "#111a27",
  surfaceHigh: "#152030",
  surfaceHover:"#192638",
  /* Borders */
  border:      "#1a2840",
  borderLight: "#243650",
  /* Text hierarchy */
  text:        "#e2edf8",
  textSub:     "#8baec9",
  textMuted:   "#3d5a78",
  /* Semantic */
  red:         "#ef4444",
  orange:      "#f59e0b",
  blue:        "#38bdf8",
  purple:      "#8b5cf6",
  cyan:        "#22d3ee",
};

/* ═══════════════════════════════════════════════════════════════
  HELPERS
═══════════════════════════════════════════════════════════════ */
const stc = (s:string) => s==="g"?JD.greenGlow:s==="a"?JD.orange:JD.red;
const stl = (s:string) => s==="g"?"جيد":s==="a"?"تحذير":"حرج";
const ndviColor = (v:number) =>
  v<.1?"#8B0000":v<.2?"#CC3300":v<.3?"#FF6600":v<.37?"#FFC107":v<.45?"#CDDC39":v<.55?"#66BB6A":"#2E7D32";

/* ═══════════════════════════════════════════════════════════════
  ATOMS
═══════════════════════════════════════════════════════════════ */

/** JD-style pill badge */
function Pill({label,color,bg,size="sm"}:{label:string;color?:string;bg?:string;size?:"xs"|"sm"}) {
  const col = color || JD.greenGlow;
  const sz = size==="xs" ? "px-1.5 py-px text-[9px]" : "px-2 py-0.5 text-[10px]";
  return (
    <span className={`inline-flex items-center rounded-sm font-bold whitespace-nowrap border ${sz}`}
      style={{background:bg||`${col}15`,color:col,borderColor:`${col}35`}}>
      {label}
    </span>
  );
}

/** Signal bar indicator */
function Signal({n}:{n:number}) {
  return (
    <div className="flex items-end gap-0.5">
      {[1,2,3,4,5].map(i=>(
        <div key={i} className="w-0.5 rounded-sm" style={{height:i*2+4,background:i<=n?JD.greenGlow:JD.textMuted}} />
      ))}
    </div>
  );
}

/** Battery indicator */
function Battery({pct}:{pct:number}) {
  const col = pct<20?JD.red:pct<40?JD.orange:JD.greenGlow;
  return (
    <div className="flex items-center gap-1">
      <div className="relative w-5 h-2.5 rounded-sm border flex overflow-hidden" style={{borderColor:col}}>
        <div className="absolute inset-0 rounded-sm" style={{width:`${pct}%`,background:col,opacity:.8}} />
      </div>
      <span className="text-[9px] font-mono" style={{color:col}}>{pct}%</span>
    </div>
  );
}

/** Slim progress bar with optimal range highlight */
function RangeBar({v,mx,opt,color}:{v:number;mx:number;opt:number[];color?:string}) {
  const pct = Math.min(100,(v/mx)*100);
  const ok = v>=opt[0] && v<=opt[1];
  const col = color || (ok?JD.greenGlow:v<opt[0]?JD.blue:JD.red);
  return (
    <div className="relative h-1.5 rounded-full overflow-hidden" style={{background:"#0a1520"}}>
      {/* optimal zone */}
      <div className="absolute top-0 h-full opacity-20" style={{left:`${(opt[0]/mx)*100}%`,width:`${((opt[1]-opt[0])/mx)*100}%`,background:col}} />
      {/* fill */}
      <div className="h-full rounded-full transition-all duration-500" style={{width:`${pct}%`,background:col}} />
    </div>
  );
}

/** Mini sparkline chart */
function Spark({data,color="#10B981",h=48}:{data:number[];color?:string;h?:number}) {
  const mx=Math.max(...data),mn=Math.min(...data),rng=mx-mn||.01;
  const pts=data.map((v,i)=>`${(i/(data.length-1))*100},${100-((v-mn)/rng)*85+5}`).join(" ");
  const uid=useRef(`g${Math.random().toString(36).slice(2)}`).current;
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full" style={{height:h}}>
      <defs>
        <linearGradient id={uid} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity=".25"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      <polygon points={`0,100 ${pts} 100,100`} fill={`url(#${uid})`}/>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="2.5" vectorEffect="non-scaling-stroke"/>
      {data.map((_,i)=>i===data.length-1?(
        <circle key={i} cx={(i/(data.length-1))*100} cy={100-((data[i]-mn)/rng)*85+5} r="3" fill={color}/>
      ):null)}
    </svg>
  );
}

/** Multi-series line chart */
function MultiLine({series,h=120}:{series:{label:string;data:number[];color:string}[];h?:number}) {
  const all=series.flatMap(s=>s.data);
  const mx=Math.max(...all),mn=Math.min(...all),rng=mx-mn||.01;
  const len=series[0]?.data.length||1;
  return (
    <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="w-full rounded-lg" style={{height:h,background:"#0a1520"}}>
      {[25,50,75].map(p=>(
        <line key={p} x1="0" y1={p} x2="100" y2={p} stroke="rgba(255,255,255,.03)" strokeWidth="0.5" vectorEffect="non-scaling-stroke"/>
      ))}
      {series.map((s,si)=>{
        const pts=s.data.map((v,i)=>`${(i/(len-1))*100},${100-((v-mn)/rng)*90}`).join(" ");
        return <polyline key={si} points={pts} fill="none" stroke={s.color} strokeWidth="2" vectorEffect="non-scaling-stroke" opacity=".9"/>;
      })}
    </svg>
  );
}

/** 9-direction field grid */
function DirGrid({alerts}:{alerts:string[]}) {
  return (
    <div className="grid grid-cols-3 gap-0.5" style={{width:108,height:108,flexShrink:0}}>
      {DIR_CELLS.map(d=>{
        const isA=alerts.includes(d.id),isC=d.id==="C";
        return (
          <div key={d.id} className="rounded flex items-center justify-center text-[8px] font-bold select-none"
            style={{
              background:isC?"rgba(16,185,129,.15)":isA?"rgba(239,68,68,.15)":"#0a1520",
              border:`1px solid ${isA?"rgba(239,68,68,.4)":isC?"rgba(16,185,129,.3)":JD.border}`,
              color:isA?JD.red:isC?JD.greenGlow:JD.textMuted,
            }}>{d.ar}</div>
        );
      })}
    </div>
  );
}

/** Section header with consistent styling */
function SectionHeader({title,sub,right}:{title:string;sub?:string;right?:React.ReactNode}) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-b" style={{borderColor:JD.border}}>
      <div>
        <div className="text-sm font-bold" style={{color:JD.text}}>{title}</div>
        {sub && <div className="text-[10px] mt-0.5" style={{color:JD.textMuted}}>{sub}</div>}
      </div>
      {right && <div className="flex items-center gap-2">{right}</div>}
    </div>
  );
}

/** JD-style primary button */
function BtnPrimary({label,onClick,icon}:{label:string;onClick?:()=>void;icon?:string}) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-bold transition-all hover:brightness-110 active:scale-95 cursor-pointer"
      style={{background:`linear-gradient(135deg,${JD.green},${JD.greenDark})`,color:"#fff",boxShadow:`0 1px 8px ${JD.green}30`}}>
      {icon && <span>{icon}</span>}{label}
    </button>
  );
}

/** JD-style ghost button */
function BtnGhost({label,onClick,icon}:{label:string;onClick?:()=>void;icon?:string}) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-bold transition-all hover:bg-white/5 active:scale-95 cursor-pointer border"
      style={{color:JD.textSub,borderColor:JD.border}}>
      {icon && <span>{icon}</span>}{label}
    </button>
  );
}

/** Filter tab strip */
function TabStrip({options,active,onChange}:{options:string[];active:string;onChange:(v:string)=>void}) {
  return (
    <div className="flex gap-0.5">
      {options.map(o=>(
        <button key={o} onClick={()=>onChange(o)}
          className="px-2.5 py-1 rounded text-[10px] font-bold transition-all cursor-pointer"
          style={{
            background:active===o?`${JD.green}15`:"transparent",
            color:active===o?JD.greenGlow:JD.textMuted,
            border:`1px solid ${active===o?`${JD.green}30`:"transparent"}`,
          }}>{o}</button>
      ))}
    </div>
  );
}

/** Card container */
function Card({children,className="",style,onClick}:{children:React.ReactNode;className?:string;style?:React.CSSProperties;onClick?:()=>void}) {
  return (
    <div onClick={onClick}
      className={`rounded-lg overflow-hidden ${className} ${onClick?"cursor-pointer hover:border-opacity-60 transition-colors":""}`}
      style={{background:JD.surface,border:`1px solid ${JD.border}`,...style}}>
      {children}
    </div>
  );
}

/** KPI stat tile — JD Operations Center style */
function KpiTile({label,value,unit,color,trend,icon}:{label:string;value:string|number;unit?:string;color?:string;trend?:number;icon?:string}) {
  const col = color || JD.greenGlow;
  return (
    <Card className="p-4">
      <div className="flex items-start justify-between mb-2">
        <span className="text-[9px] uppercase tracking-widest font-bold" style={{color:JD.textMuted}}>{label}</span>
        {icon && <span className="text-sm" style={{color:`${col}50`}}>{icon}</span>}
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-black tabular-nums leading-none" style={{color:col}}>{value}</span>
        {unit && <span className="text-[10px]" style={{color:JD.textMuted}}>{unit}</span>}
      </div>
      {trend!==undefined && (
        <div className="text-[9px] mt-1.5 flex items-center gap-1" style={{color:trend>0?JD.greenGlow:JD.red}}>
          <span>{trend>0?"↑":"↓"} {Math.abs(trend)}%</span>
          <span style={{color:JD.textMuted}}>من الأسبوع الماضي</span>
        </div>
      )}
    </Card>
  );
}

/* ═══════════════════════════════════════════════════════════════
  LOGO
═══════════════════════════════════════════════════════════════ */
function SahoolLogo({collapsed}:{collapsed:boolean}) {
  return (
    <div className="flex items-center gap-2.5 select-none">
      <div className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
        style={{background:`linear-gradient(135deg,${JD.green},${JD.greenDark})`,boxShadow:`0 0 16px ${JD.green}40`}}>
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M12 3C10.5 5.5 8 7.5 8 11c0 2.2 1.8 4 4 4s4-1.8 4-4c0-3.5-2.5-5.5-4-8z" fill={JD.yellow}/>
          <path d="M9 13.5c-.4 1.6-.4 3 0 4.5M15 13.5c.4 1.6.4 3 0 4.5M12 15.5v6.5" stroke="#A8DDA0" strokeWidth="1.6" strokeLinecap="round"/>
        </svg>
      </div>
      {!collapsed && (
        <div>
          <div className="text-sm font-black tracking-[.12em] leading-none" style={{color:JD.greenGlow}}>SAHOOL</div>
          <div className="text-[9px] tracking-wider mt-0.5" style={{color:JD.textMuted}}>سهول · الزراعة الذكية</div>
        </div>
      )}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  SIDEBAR — John Deere Operations Center nav style
═══════════════════════════════════════════════════════════════ */
function Sidebar({active,go,collapsed,setCollapsed}:{
  active:ScreenId;go:(s:ScreenId)=>void;collapsed:boolean;setCollapsed:(v:boolean)=>void;
}) {
  const groups = [...new Set(SCREENS.map(s=>s.group))];

  return (
    <aside className="h-screen flex-shrink-0 flex flex-col transition-all duration-300"
      style={{
        width:collapsed?56:220,
        background:"#080e1a",
        borderLeft:`1px solid ${JD.border}`,
        zIndex:20,
      }}>

      {/* Logo area */}
      <div className="flex items-center px-3 border-b" style={{borderColor:JD.border,height:56}}>
        <SahoolLogo collapsed={collapsed}/>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-2 scrollbar-thin" style={{scrollbarWidth:"none"}}>
        {groups.map(group=>{
          const items = SCREENS.filter(s=>s.group===group);
          return (
            <div key={group} className="mb-1">
              {!collapsed && (
                <div className="px-3 py-1.5 text-[8px] uppercase tracking-[.15em] font-bold" style={{color:JD.textMuted}}>
                  {group}
                </div>
              )}
              {items.map(s=>{
                const isOn = active===s.id;
                return (
                  <button key={s.id} onClick={()=>go(s.id as ScreenId)}
                    title={collapsed?s.label:undefined}
                    className={`w-full flex items-center transition-all duration-150 cursor-pointer ${collapsed?"justify-center py-2.5":"gap-2.5 px-3 py-2"}`}
                    style={{
                      background:isOn?`${JD.green}12`:"transparent",
                      color:isOn?JD.greenGlow:JD.textMuted,
                      borderRight:isOn?`2px solid ${JD.greenGlow}`:"2px solid transparent",
                    }}>
                    <span className={`${collapsed?"text-lg":"text-sm"} flex-shrink-0 leading-none`}>{s.ic}</span>
                    {!collapsed && <span className="text-[11px] font-medium whitespace-nowrap">{s.label}</span>}
                  </button>
                );
              })}
            </div>
          );
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="p-2 border-t" style={{borderColor:JD.border}}>
        <button onClick={()=>setCollapsed(!collapsed)}
          className="w-full flex items-center justify-center p-1.5 rounded text-[10px] transition-colors cursor-pointer hover:bg-white/5"
          style={{color:JD.textMuted}}>
          {collapsed?"→":"← طي"}
        </button>
      </div>
    </aside>
  );
}

/* ═══════════════════════════════════════════════════════════════
  TOPBAR
═══════════════════════════════════════════════════════════════ */
function TopBar({label,alertCount}:{label:string;alertCount:number}) {
  return (
    <header className="flex-shrink-0 h-14 flex items-center justify-between px-5 border-b"
      style={{background:"#080e1a",borderColor:JD.border}}>
      {/* Breadcrumb */}
      <div className="flex items-center gap-2">
        <span className="text-[10px]" style={{color:JD.textMuted}}>SAHOOL</span>
        <span style={{color:JD.textMuted}}>/</span>
        <span className="text-sm font-bold" style={{color:JD.text}}>{label}</span>
        <Pill label="مباشر" color={JD.greenGlow}/>
      </div>

      {/* Right actions */}
      <div className="flex items-center gap-3">
        {/* Alert bell */}
        <button className="relative p-1.5 rounded transition-colors hover:bg-white/5 cursor-pointer" style={{color:JD.textSub}}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 01-3.46 0"/>
          </svg>
          {alertCount>0 && (
            <span className="absolute top-0.5 right-0.5 w-3.5 h-3.5 rounded-full text-[8px] font-black flex items-center justify-center"
              style={{background:JD.red,color:"#fff"}}>{alertCount}</span>
          )}
        </button>

        {/* Live indicator */}
        <div className="flex items-center gap-1.5 text-[10px]" style={{color:JD.textMuted}}>
          <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{background:JD.greenGlow,animationDuration:"2s"}}/>
          <span>03-05-2026</span>
        </div>

        {/* User avatar */}
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-black"
            style={{background:`${JD.yellow}18`,color:JD.yellow,border:`1px solid ${JD.yellow}30`}}>
            ع
          </div>
          <div className="hidden md:block">
            <div className="text-[10px] font-bold leading-none" style={{color:JD.text}}>عادل المطهر</div>
            <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>مسؤول المزرعة</div>
          </div>
        </div>
      </div>
    </header>
  );
}

          <div className="text-xs font-bold mb-3" style={{color:JD.text}}>خريطة المناطق — {type}</div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {["حقل الشمال","الوادي الأوسط"].map(f=>{
              const fz=zones.filter(z=>z.field===f);
              return (
                <div key={f} className="rounded-md p-3" style={{background:"#0a1520",border:`1px solid ${JD.border}`}}>
                  <div className="text-[11px] font-bold mb-2.5" style={{color:JD.text}}>{f}</div>
                  <div className="flex gap-2">
                    {fz.map(z=>{
                      return (
                        <div key={z.id} className="flex-1 rounded-md p-2 text-center" style={{background:`${z.color}10`,border:`1px solid ${z.color}30`}}>
                          <div className="text-[9px] font-bold mb-1" style={{color:z.color}}>{z.zone}</div>
                          <div className="text-xl font-black tabular-nums" style={{color:z.color}}>{z.rate}</div>
                          <div className="text-[8px]" style={{color:JD.textMuted}}>{z.unit}</div>
                          <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>{z.area} هـ</div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-3 rounded-md p-2.5 flex gap-4" style={{background:"#0a1520"}}>
            {[{c:"#EF4444",l:"منخفضة — جرعة عالية"},{c:"#F59E0B",l:"متوسطة — جرعة متوسطة"},{c:"#10B981",l:"عالية — جرعة منخفضة"}].map(lv=>{
              return (
                <div key={lv.l} className="flex items-center gap-1.5">
                  <div className="w-2.5 h-2.5 rounded-sm" style={{background:lv.c}}/>
                  <span className="text-[9px]" style={{color:JD.textSub}}>{lv.l}</span>
                </div>
              );
            })}
          </div>
        </Card>

        <div className="flex flex-col gap-3">
          <Card className="p-4">
            <div className="text-xs font-bold mb-3" style={{color:JD.text}}>ملخص الجرعات</div>
            {[{l:"إجمالي المساحة",v:"6.2 هـ"},{l:"متوسط الجرعة",v:"113 كغ/هـ"},{l:"الكمية الإجمالية",v:"700 كغ"},{l:"التوفير المتوقع",v:"12%"}].map(s=>{
              return (
                <div key={s.l} className="flex justify-between py-2" style={{borderBottom:`1px solid ${JD.border}`}}>
                  <span className="text-[10px]" style={{color:JD.textMuted}}>{s.l}</span>
                  <span className="text-[10px] font-black tabular-nums" style={{color:JD.text}}>{s.v}</span>
                </div>
              );
            })}
          </Card>

          <Card className="p-4">
            <div className="text-xs font-bold mb-2" style={{color:JD.text}}>متوافق مع</div>
            <div className="flex flex-wrap gap-1.5">
              {["John Deere","Trimble","ISO-XML","Shapefile","KML"].map(b=>{
                return <Pill key={b} label={b} size="xs"/>;
              })}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  TRACE
═══════════════════════════════════════════════════════════════ */
function Dashboard({fields,go}:{fields:Field[];go:(s:ScreenId)=>void}) {
const ndviData = [.32,.36,.39,.38,.42,.44,.47,.45,.48,.44,.50,.53];
const alertFields = fields.filter(f=>f.st!==“g”);
const todayTasks = TASKS.filter(t=>t.due===“اليوم”&&!t.done);

return (
<div className="flex flex-col gap-4">
{/* KPI strip */}
<div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
<KpiTile label="إجمالي الحقول" value={fields.length} unit="حقل" color={JD.greenGlow} icon="◎" trend={0}/>
<KpiTile label="تنبيهات نشطة" value={alertFields.length} unit="تنبيه" color={JD.red} icon="◈" trend={-12}/>
<KpiTile label="مهام اليوم" value={todayTasks.length} unit="مهمة" color={JD.orange} icon="◻" trend={0}/>
<KpiTile label=“متوسط NDVI” value={Math.round(fields.reduce((a,f)=>a+f.ndvi,0)/fields.length*100)} unit=”%” color={JD.cyan} icon=“✾” trend={5}/>
</div>

```
  {/* Main grid */}
  <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-4">

    {/* Fields table */}
    <Card>
      <SectionHeader
        title="◎ حقول المزرعة"
        sub={`${fields.length} حقول · تحديث كل 5 أيام`}
        right={<>
          <BtnGhost label="🗺 الخريطة" onClick={()=>go("map")}/>
          <BtnPrimary label="📄 تقرير" onClick={()=>go("rep")}/>
        </>}
      />
      <div className="overflow-x-auto">
        <table className="w-full text-[11px]">
          <thead>
            <tr style={{background:"#0a1520"}}>
              {["الحقل","المحصول","المساحة","NDVI","رطوبة","EC","الحالة","التنبيهات"].map(h=>(
                <th key={h} className="px-3 py-2.5 text-right font-bold whitespace-nowrap border-b"
                  style={{color:JD.textMuted,borderColor:JD.border,fontSize:9,letterSpacing:".05em"}}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {fields.map((f,i)=>(
              <tr key={f.id} className="border-b transition-colors hover:bg-white/[.015] cursor-pointer"
                style={{borderColor:i<fields.length-1?JD.border:"transparent"}}
                onClick={()=>go("rep")}>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-sm flex-shrink-0" style={{background:stc(f.st),boxShadow:`0 0 6px ${stc(f.st)}60`}}/>
                    <span className="font-bold" style={{color:JD.text}}>{f.n}</span>
                  </div>
                </td>
                <td className="px-3 py-3" style={{color:JD.textSub}}>{f.crop}</td>
                <td className="px-3 py-3 tabular-nums" style={{color:JD.textSub}}>{f.area} هـ</td>
                <td className="px-3 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-1 rounded-sm" style={{background:"#0a1520"}}>
                      <div className="h-full rounded-sm" style={{width:`${f.ndvi*100}%`,background:ndviColor(f.ndvi)}}/>
                    </div>
                    <span className="font-black tabular-nums text-[10px]" style={{color:ndviColor(f.ndvi)}}>{f.ndvi}</span>
                  </div>
                </td>
                <td className="px-3 py-3 font-bold tabular-nums" style={{color:f.moist<35?JD.red:f.moist>65?JD.orange:JD.greenGlow}}>{f.moist}%</td>
                <td className="px-3 py-3 font-bold tabular-nums" style={{color:f.ec>2?JD.red:f.ec>1.5?JD.orange:JD.greenGlow}}>{f.ec}</td>
                <td className="px-3 py-3"><Pill label={stl(f.st)} color={stc(f.st)}/></td>
                <td className="px-3 py-3 text-[10px]" style={{color:f.dir.length?JD.red:JD.textMuted}}>
                  {f.dir.length>0?f.dir.join(", "):"—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>

    {/* Right column */}
    <div className="flex flex-col gap-3">

      {/* NDVI trend */}
      <Card className="p-4">
        <div className="flex justify-between items-center mb-3">
          <div>
            <div className="text-xs font-bold" style={{color:JD.text}}>NDVI الأسبوعي</div>
            <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>12 أسبوعاً · حقل الشمال</div>
          </div>
          <span className="font-black tabular-nums" style={{color:ndviColor(.53)}}>.53 ↑</span>
        </div>
        <Spark data={ndviData} color="#10B981" h={52}/>
      </Card>

      {/* GDD progress */}
      <Card className="p-4">
        <div className="flex justify-between items-start mb-3">
          <div>
            <div className="text-xs font-bold" style={{color:JD.text}}>GDD — درجات النمو</div>
            <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>FAO Base-10</div>
          </div>
          <div className="text-left">
            <div className="text-xl font-black tabular-nums leading-none" style={{color:JD.orange}}>1,650</div>
            <div className="text-[9px]" style={{color:JD.textMuted}}>/ 2,100</div>
          </div>
        </div>
        <div className="h-1.5 rounded-full overflow-hidden mb-2" style={{background:"#0a1520"}}>
          <div className="h-full rounded-full" style={{width:"78.6%",background:`linear-gradient(90deg,${JD.orange},${JD.greenGlow})`}}/>
        </div>
        <div className="flex justify-between text-[9px]" style={{color:JD.textMuted}}>
          <span>إنبات</span><span>تفريع</span><span>إزهار ←</span><span>نضج</span>
        </div>
      </Card>

      {/* Spray windows */}
      <Card>
        <SectionHeader title="نوافذ الرش — اليوم"/>
        <div className="p-3 space-y-1">
          {[
            {t:"06:00–08:00",ok:true, w:"1.8 م/ث",h:"68%",note:"مثالي"},
            {t:"12:00–16:00",ok:false,w:"5.4 م/ث",h:"41%",note:"رياح قوية"},
            {t:"17:00–19:30",ok:true, w:"2.1 م/ث",h:"62%",note:"جيد"},
          ].map((s,i)=>(
            <div key={i} className="flex items-center gap-2.5 rounded p-2.5"
              style={{background:s.ok?"rgba(16,185,129,.06)":"rgba(239,68,68,.05)",border:`1px solid ${s.ok?"rgba(16,185,129,.15)":"rgba(239,68,68,.1)"}`}}>
              <div className="w-4 h-4 rounded-sm flex items-center justify-center flex-shrink-0"
                style={{background:s.ok?"rgba(16,185,129,.15)":"rgba(239,68,68,.1)"}}>
                <span className="text-[9px] font-black" style={{color:s.ok?JD.greenGlow:JD.red}}>{s.ok?"✓":"✕"}</span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-bold" style={{color:JD.text}}>{s.t}</div>
                <div className="text-[9px]" style={{color:JD.textMuted}}>رياح: {s.w} · رطوبة: {s.h}</div>
              </div>
              <Pill label={s.note} color={s.ok?JD.greenGlow:JD.red} size="xs"/>
            </div>
          ))}
        </div>
      </Card>
    </div>
  </div>

  {/* Hybrid scale */}
  <Card>
    <SectionHeader
      title="مقياس Hybrid — صحة المحصول والري"
      sub="5 ألوان · الافتراضي للمزارع"
      right={<BtnGhost label="عرض كل المؤشرات (16)" onClick={()=>go("idx")}/>}
    />
    <div className="p-4 grid grid-cols-2 md:grid-cols-5 gap-3">
      {HYBRID_SCALE.map(h=>(
        <div key={h.label}>
          <div className="h-6 rounded-sm mb-2" style={{background:h.c,boxShadow:`0 0 8px ${h.c}30`}}/>
          <div className="text-[10px] leading-snug" style={{color:JD.textSub}}>{h.label}</div>
          <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{h.en}</div>
        </div>
      ))}
    </div>
  </Card>

  {/* Alert cards */}
  {alertFields.length>0 && (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      {alertFields.map(f=>(
        <div key={f.id} className="rounded-lg p-4 flex gap-4"
          style={{background:"rgba(239,68,68,.04)",border:"1px solid rgba(239,68,68,.18)"}}>
          <DirGrid alerts={f.dir}/>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <div className="text-sm font-bold" style={{color:JD.text}}>{f.n}</div>
              <Pill label={f.crop} size="xs"/>
            </div>
            <div className="text-[10px] mb-2" style={{color:JD.textMuted}}>{f.area} هـ · NDVI: {f.ndvi}</div>
            {f.dir.length>0 && (
              <div className="text-[10px] leading-relaxed mb-2" style={{color:JD.red}}>
                ⚠ فحص مطلوب: <strong>{f.dir.map(d=>DIR_CELLS.find(c=>c.id===d)?.ar).join(" · ")}</strong>
              </div>
            )}
            <BtnGhost label="عرض التقرير" onClick={()=>go("rep")}/>
          </div>
        </div>
      ))}
    </div>
  )}
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
MAP
═══════════════════════════════════════════════════════════════ */
function getFieldOverlayColor(indexId: string, ndvi: number): string {
  switch(indexId) {
    case "hybrid":
      if (ndvi >= 0.7) return "rgba(16,185,129,0.55)";
      if (ndvi >= 0.5) return "rgba(249,115,22,0.50)";
      if (ndvi >= 0.3) return "rgba(139,92,246,0.50)";
      return "rgba(239,68,68,0.55)";
    case "ndvi": return `${ndviColor(ndvi)}88`;
    case "evi": return ndvi >= 0.6 ? "rgba(74,222,128,0.60)" : "rgba(74,222,128,0.30)";
    case "savi": return ndvi >= 0.5 ? "rgba(134,239,172,0.55)" : "rgba(134,239,172,0.25)";
    case "ndre": return ndvi >= 0.7 ? "rgba(163,230,53,0.60)" : "rgba(163,230,53,0.30)";
    case "ndwi": return ndvi >= 0.5 ? "rgba(56,189,248,0.55)" : "rgba(56,189,248,0.25)";
    case "et": return ndvi >= 0.4 ? "rgba(125,211,252,0.50)" : "rgba(125,211,252,0.25)";
    case "ndmi": return ndvi >= 0.4 ? "rgba(186,230,253,0.50)" : "rgba(186,230,253,0.25)";
    case "soc": return ndvi >= 0.5 ? "rgba(217,119,6,0.50)" : "rgba(217,119,6,0.25)";
    case "erosion": return "rgba(239,68,68,0.40)";
    case "dem": return `rgba(139,92,246,${0.2 + ndvi * 0.4})`;
    case "rvi": return ndvi >= 0.5 ? "rgba(245,158,11,0.55)" : "rgba(245,158,11,0.30)";
    case "rsm": return ndvi >= 0.4 ? "rgba(252,211,77,0.50)" : "rgba(252,211,77,0.25)";
    case "tci": return "rgba(14,165,233,0.20)";
    case "etci": return "rgba(56,189,248,0.25)";
    case "cb": return "rgba(148,163,184,0.30)";
    default: return `${ndviColor(ndvi)}88`;
  }
}

function getFieldBorderColor(indexId: string, ndvi: number): string {
  switch(indexId) {
    case "hybrid":
      if (ndvi >= 0.7) return "#10B981";
      if (ndvi >= 0.5) return "#F97316";
      if (ndvi >= 0.3) return "#8B5CF6";
      return "#EF4444";
    case "ndvi": return ndviColor(ndvi);
    case "evi": return "#4ADE80";
    case "savi": return "#86EFAC";
    case "ndre": return "#A3E635";
    case "ndwi": return "#38BDF8";
    case "et": return "#7DD3FC";
    case "ndmi": return "#BAE6FD";
    case "soc": return "#D97706";
    case "erosion": return "#EF4444";
    case "dem": return "#8B5CF6";
    case "rvi": return "#F59E0B";
    case "rsm": return "#FCD34D";
    case "tci": return "#0EA5E9";
    case "etci": return "#38BDF8";
    case "cb": return "#94A3B8";
    default: return ndviColor(ndvi);
  }
}

/* ═══════════════════════════════════════════════════════════════
  MAP SCREEN — John Deere Operations Center Style
  with proper index overlay visualization
═══════════════════════════════════════════════════════════════ */
interface Field {id:number;n:string;crop:string;area:string;ndvi:number;ec:number;moist:number;elev:number;st:string;dir:string[];lat:number;lng:number;}

function MapScreen({field, fields}: {field?: Field; fields: Field[]}) {
  const [selIdx, setSelIdx] = useState("hybrid");
  const [selField, setSelField] = useState<Field | undefined>(FIELDS[0]);
  const [layer, setLayer] = useState("Satellite");
  const [showLabels, setShowLabels] = useState(true);
  const [showGrid, setShowGrid] = useState(false);
  const [opacity, setOpacity] = useState(0.65);
  const [zoom, setZoom] = useState(1);
  const idxInfo = ALL_INDICES.find(i => i.id === selIdx) || ALL_INDICES[0];

  // JD Operations Center style color scale
  const SCALE = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8];

  // Field positions on map (percentage-based)
  const fieldPositions = [
    { top: "18%", left: "28%", w: "20%", h: "16%", rot: -5 },
    { top: "34%", left: "52%", w: "16%", h: "20%", rot: 8 },
    { top: "54%", left: "18%", w: "24%", h: "18%", rot: -3 },
    { top: "66%", left: "66%", w: "13%", h: "14%", rot: 12 },
    { top: "44%", left: "40%", w: "18%", h: "16%", rot: 5 },
  ];

  return (
    <div className="flex flex-col gap-3 h-full" style={{ direction: "rtl" }}>

      {/* ═══ TOP CONTROL BAR ═══ */}
      <Card>
        <div className="p-2.5 flex gap-2 items-center flex-wrap">
          {/* Layer selector */}
          <div className="flex gap-0.5 bg-black/20 rounded p-0.5">
            {["Satellite", "Map", "Hybrid"].map(l => {
              const isActive = layer === l;
              return (
                <button key={l} onClick={() => setLayer(l)}
                  className="px-3 py-1.5 rounded text-[10px] font-bold transition-all cursor-pointer"
                  style={{
                    background: isActive ? JD.green : "transparent",
                    color: isActive ? "#fff" : JD.textMuted,
                  }}>{l}</button>
              );
            })}
          </div>

          <div className="w-px h-5 mx-1" style={{ background: JD.border }} />

          {/* Index selector — horizontal scrollable */}
          <div className="flex gap-1 overflow-x-auto flex-1" style={{ scrollbarWidth: "none" }}>
            {ALL_INDICES.map(i => {
              const isActive = selIdx === i.id;
              return (
                <button key={i.id} onClick={() => setSelIdx(i.id)}
                  className="px-2.5 py-1 rounded text-[10px] font-bold transition-all cursor-pointer whitespace-nowrap border flex items-center gap-1"
                  style={{
                    background: isActive ? `${i.c}18` : "transparent",
                    color: isActive ? i.c : JD.textMuted,
                    borderColor: isActive ? `${i.c}40` : "transparent",
                  }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: i.c, boxShadow: isActive ? `0 0 4px ${i.c}` : "none" }} />
                  {i.lab}
                </button>
              );
            })}
          </div>

          <div className="w-px h-5 mx-1" style={{ background: JD.border }} />

          {/* Toggles */}
          <div className="flex gap-2 items-center">
            <label className="flex items-center gap-1 text-[9px] cursor-pointer" style={{ color: JD.textMuted }}>
              <input type="checkbox" checked={showLabels} onChange={e => setShowLabels(e.target.checked)} className="w-3 h-3" />
              التسميات
            </label>
            <label className="flex items-center gap-1 text-[9px] cursor-pointer" style={{ color: JD.textMuted }}>
              <input type="checkbox" checked={showGrid} onChange={e => setShowGrid(e.target.checked)} className="w-3 h-3" />
              الشبكة
            </label>
          </div>

          <div className="mr-auto flex gap-2">
            <BtnGhost label="⬇ KML/SHP" />
            <BtnPrimary label="+ إضافة حقل" />
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-3 flex-1 min-h-0">

        {/* ═══ MAP VIEWPORT ═══ */}
        <div className="rounded-lg overflow-hidden relative min-h-[480px]"
          style={{ background: JD.surface, border: `1px solid ${JD.border}` }}>

          {/* Satellite base layer */}
          <div className="absolute inset-0" 
            style={{ 
              background: layer === "Map" 
                ? "#1a2332" 
                : "radial-gradient(ellipse at 45% 40%, #2d4a1e 0%, #1a3010 30%, #0d1a08 60%, #050a04 100%)",
            }} />

          {/* Terrain texture for Satellite/Hybrid */}
          {(layer === "Satellite" || layer === "Hybrid") && (
            <>
              {/* Grid pattern for fields */}
              <svg className="absolute inset-0 w-full h-full opacity-[0.08]" preserveAspectRatio="none">
                <defs>
                  <pattern id="fieldGrid" width="40" height="40" patternUnits="userSpaceOnUse">
                    <path d="M40 0L0 0 0 40" fill="none" stroke="#7CB342" strokeWidth="0.5"/>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#fieldGrid)"/>
              </svg>

              {/* Road lines simulation */}
              <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none">
                <line x1="0" y1="50%" x2="100%" y2="50%" stroke="rgba(180,160,100,0.15)" strokeWidth="1.5" strokeDasharray="8,4"/>
                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(180,160,100,0.12)" strokeWidth="1"/>
                <line x1="25%" y1="0" x2="25%" y2="100%" stroke="rgba(180,160,100,0.08)" strokeWidth="0.8"/>
                <line x1="75%" y1="0" x2="75%" y2="100%" stroke="rgba(180,160,100,0.08)" strokeWidth="0.8"/>
              </svg>

              {/* Water bodies simulation */}
              <div className="absolute rounded-full opacity-20" 
                style={{ top: "8%", left: "65%", width: "12%", height: "8%", background: "radial-gradient(circle, #1e5a8a, #0d2d4a)" }} />
            </>
          )}

          {/* Optional grid overlay */}
          {showGrid && (
            <svg className="absolute inset-0 w-full h-full pointer-events-none" preserveAspectRatio="none">
              <defs>
                <pattern id="coordGrid" width="60" height="60" patternUnits="userSpaceOnUse">
                  <path d="M60 0L0 0 0 60" fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="0.5"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#coordGrid)"/>
            </svg>
          )}

          {/* ═══ FIELD POLYGONS WITH INDEX OVERLAY ═══ */}
          {FIELDS.map((f, idx) => {
            const pos = fieldPositions[idx];
            const isSelected = selField?.id === f.id;
            const overlayColor = getFieldOverlayColor(selIdx, f.ndvi);
            const borderColor = getFieldBorderColor(selIdx, f.ndvi);
            const glowColor = borderColor + "40";

            return (
              <div key={f.id} onClick={() => setSelField(f)}
                className="absolute cursor-pointer transition-all duration-300"
                style={{
                  top: pos.top,
                  left: pos.left,
                  width: pos.w,
                  height: pos.h,
                  transform: `rotate(${pos.rot}deg) scale(${isSelected ? 1.02 : 1})`,
                  zIndex: isSelected ? 20 : 10,
                }}>

                {/* Field polygon shape */}
                <div className="absolute inset-0 rounded-sm"
                  style={{
                    background: overlayColor,
                    border: `${isSelected ? 2.5 : 1.5}px solid ${isSelected ? JD.yellow : borderColor}`,
                    boxShadow: isSelected 
                      ? `0 0 0 4px ${JD.yellow}30, 0 0 20px ${glowColor}` 
                      : `0 0 8px ${glowColor}`,
                    opacity: opacity,
                  }} />

                {/* Inner texture pattern for realism */}
                <div className="absolute inset-1 rounded-sm opacity-30"
                  style={{
                    background: `repeating-linear-gradient(
                      ${45 + pos.rot}deg,
                      transparent,
                      transparent 3px,
                      rgba(0,0,0,0.1) 3px,
                      rgba(0,0,0,0.1) 6px
                    )`,
                  }} />

                {/* Field label */}
                {showLabels && (
                  <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
                    style={{ transform: `rotate(${-pos.rot}deg)` }}>
                    <div className="text-center">
                      <div className="text-[10px] font-black px-1.5 py-0.5 rounded-sm"
                        style={{ 
                          color: "#fff", 
                          background: "rgba(0,0,0,0.6)",
                          textShadow: "0 1px 3px rgba(0,0,0,0.9)",
                        }}>
                        {f.n}
                      </div>
                      <div className="text-[9px] font-bold mt-0.5 px-1 py-px rounded-sm inline-block"
                        style={{ 
                          color: borderColor, 
                          background: "rgba(0,0,0,0.7)",
                        }}>
                        {selIdx === "hybrid" ? (
                          f.ndvi >= 0.7 ? "ممتاز" : f.ndvi >= 0.5 ? "انتباه" : f.ndvi >= 0.3 ? "ري" : "حرج"
                        ) : (
                          `${f.ndvi}`
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Alert indicator */}
                {f.st !== "g" && (
                  <div className="absolute -top-2 -right-2 w-5 h-5 rounded-full flex items-center justify-center animate-pulse"
                    style={{ 
                      background: stc(f.st), 
                      border: `2px solid ${JD.panel}`,
                      boxShadow: `0 0 8px ${stc(f.st)}`,
                    }}>
                    <span className="text-[8px] text-white font-black">!</span>
                  </div>
                )}

                {/* Selection halo */}
                {isSelected && (
                  <div className="absolute -inset-1 rounded-md pointer-events-none"
                    style={{
                      border: `2px dashed ${JD.yellow}60`,
                      animation: "pulse 2s infinite",
                    }} />
                )}
              </div>
            );
          })}

          {/* ═══ BOTTOM LEFT: INDEX LEGEND ═══ */}
          <div className="absolute bottom-4 left-4 rounded-lg p-3 flex flex-col gap-2"
            style={{ background: "rgba(5,10,20,0.92)", border: `1px solid ${JD.border}`, backdropFilter: "blur(8px)" }}>

            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 rounded-sm" style={{ background: idxInfo.c }} />
              <span className="text-[10px] font-bold" style={{ color: JD.text }}>{idxInfo.lab}</span>
              <span className="text-[8px] px-1.5 py-px rounded-sm" style={{ color: idxInfo.c, background: `${idxInfo.c}15` }}>{idxInfo.cat}</span>
            </div>

            {/* Color scale bar */}
            <div className="flex gap-px rounded-sm overflow-hidden" style={{ height: 14 }}>
              {SCALE.map(v => (
                <div key={v} className="flex-1" style={{ background: getFieldBorderColor(selIdx, v) }} />
              ))}
            </div>
            <div className="flex justify-between text-[7px] font-mono" style={{ color: "rgba(255,255,255,0.4)" }}>
              <span>0.0</span>
              <span>0.2</span>
              <span>0.4</span>
              <span>0.6</span>
              <span>0.8</span>
            </div>

            {/* Opacity slider */}
            <div className="flex items-center gap-2 mt-1">
              <span className="text-[8px]" style={{ color: JD.textMuted }}>الشفافية</span>
              <input 
                type="range" 
                min="0.2" 
                max="1" 
                step="0.05" 
                value={opacity}
                onChange={e => setOpacity(parseFloat(e.target.value))}
                className="flex-1 h-1 rounded-full appearance-none cursor-pointer"
                style={{ 
                  background: `linear-gradient(to left, ${JD.green}, ${JD.border})`,
                  accentColor: JD.green,
                }}
              />
              <span className="text-[8px] font-mono w-8 text-left" style={{ color: JD.textMuted }}>{Math.round(opacity * 100)}%</span>
            </div>
          </div>

          {/* ═══ TOP LEFT: LAYER BADGE ═══ */}
          <div className="absolute top-4 left-4 rounded-lg px-3 py-2 flex items-center gap-2"
            style={{ background: "rgba(5,10,20,0.88)", border: `1px solid ${JD.border}` }}>
            <span className="text-sm">🛰</span>
            <div>
              <div className="text-[9px] font-bold" style={{ color: JD.text }}>24-03-2026</div>
              <div className="text-[8px]" style={{ color: JD.textMuted }}>{layer} · Sentinel-2 · 10م/بكسل</div>
            </div>
          </div>

          {/* ═══ TOP RIGHT: ZOOM CONTROLS ═══ */}
          <div className="absolute top-4 right-4 flex flex-col gap-1">
            <button onClick={() => setZoom(Math.min(zoom + 0.25, 2.5))}
              className="w-8 h-8 rounded flex items-center justify-center text-lg font-bold cursor-pointer transition-all hover:brightness-125"
              style={{ background: "rgba(5,10,20,0.88)", border: `1px solid ${JD.border}`, color: JD.text }}>+</button>
            <div className="text-center text-[9px] font-mono py-1 rounded"
              style={{ background: "rgba(5,10,20,0.88)", border: `1px solid ${JD.border}`, color: JD.textMuted }}>
              {Math.round(zoom * 100)}%
            </div>
            <button onClick={() => setZoom(Math.max(zoom - 0.25, 0.5))}
              className="w-8 h-8 rounded flex items-center justify-center text-lg font-bold cursor-pointer transition-all hover:brightness-125"
              style={{ background: "rgba(5,10,20,0.88)", border: `1px solid ${JD.border}`, color: JD.text }}>−</button>
          </div>

          {/* ═══ BOTTOM RIGHT: MINI MAP / OVERVIEW ═══ */}
          <div className="absolute bottom-4 right-4 rounded-lg overflow-hidden"
            style={{ width: 140, height: 100, background: "rgba(5,10,20,0.9)", border: `1px solid ${JD.border}` }}>
            <div className="text-[8px] font-bold px-2 py-1" style={{ color: JD.textMuted, background: "rgba(0,0,0,0.3)" }}>نظرة عامة</div>
            <div className="relative w-full h-full">
              {FIELDS.map((f, idx) => {
                const pos = fieldPositions[idx];
                return (
                  <div key={f.id} 
                    className="absolute rounded-sm cursor-pointer"
                    onClick={() => setSelField(f)}
                    style={{
                      top: pos.top,
                      left: pos.left,
                      width: `calc(${pos.w} * 0.6)`,
                      height: `calc(${pos.h} * 0.6)`,
                      background: getFieldOverlayColor(selIdx, f.ndvi),
                      border: `1px solid ${selField?.id === f.id ? JD.yellow : getFieldBorderColor(selIdx, f.ndvi)}`,
                      opacity: 0.8,
                    }} />
                );
              })}
            </div>
          </div>

          {/* ═══ CENTER: CROSSHAIR (optional) ═══ */}
          <div className="absolute top-1/2 left-1/2 pointer-events-none"
            style={{ transform: "translate(-50%, -50%)" }}>
            <div className="w-4 h-4 rounded-full border"
              style={{ borderColor: "rgba(255,255,255,0.15)" }}>
              <div className="absolute top-1/2 left-0 w-full h-px" style={{ background: "rgba(255,255,255,0.1)" }} />
              <div className="absolute top-0 left-1/2 w-px h-full" style={{ background: "rgba(255,255,255,0.1)" }} />
            </div>
          </div>
        </div>

        {/* ═══ RIGHT PANEL: FIELD DETAILS ═══ */}
        <div className="flex flex-col gap-3 overflow-y-auto" style={{ scrollbarWidth: "none" }}>

          {/* Selected field card */}
          {selField && (
            <Card style={{ borderTop: `3px solid ${getFieldBorderColor(selIdx, selField.ndvi)}` }}>
              <div className="p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="text-sm font-bold" style={{ color: JD.text }}>{selField.n}</div>
                    <div className="text-[10px] mt-0.5" style={{ color: JD.textMuted }}>{selField.crop} · {selField.area} هـ · {selField.elev}م</div>
                  </div>
                  <Pill 
                    label={selField.st === "g" ? "جيد" : selField.st === "a" ? "تحذير" : "حرج"} 
                    color={stc(selField.st)} 
                  />
                </div>

                {/* Index value display */}
                <div className="rounded-lg p-3 mb-3 text-center"
                  style={{ background: `${getFieldBorderColor(selIdx, selField.ndvi)}10`, border: `1px solid ${getFieldBorderColor(selIdx, selField.ndvi)}30` }}>
                  <div className="text-[9px] font-bold mb-1" style={{ color: JD.textMuted }}>{idxInfo.lab} الحالي</div>
                  <div className="text-2xl font-black tabular-nums" style={{ color: getFieldBorderColor(selIdx, selField.ndvi) }}>
                    {selIdx === "hybrid" ? (
                      selField.ndvi >= 0.7 ? "ممتاز" : selField.ndvi >= 0.5 ? "انتباه" : selField.ndvi >= 0.3 ? "ري" : "حرج"
                    ) : (
                      selField.ndvi
                    )}
                  </div>
                </div>

                {/* Metrics bars */}
                {[
                  { label: "NDVI صحة", v: selField.ndvi * 100, mx: 100, opt: [40, 80], c: ndviColor(selField.ndvi) },
                  { label: "رطوبة التربة", v: selField.moist, mx: 100, opt: [35, 65], c: selField.moist < 35 ? JD.red : selField.moist > 65 ? JD.orange : JD.greenGlow },
                  { label: "EC الملوحة", v: selField.ec, mx: 5, opt: [0.5, 2], c: selField.ec > 2 ? JD.red : selField.ec > 1.5 ? JD.orange : JD.greenGlow },
                ].map(row => (
                  <div key={row.label} className="mb-2.5">
                    <div className="flex justify-between text-[9px] mb-1">
                      <span style={{ color: JD.textMuted }}>{row.label}</span>
                      <span className="font-black tabular-nums" style={{ color: row.c }}>
                        {row.label.includes("NDVI") ? selField.ndvi : row.label.includes("رطوبة") ? `${selField.moist}%` : `${selField.ec} dS/m`}
                      </span>
                    </div>
                    <div className="relative h-1.5 rounded-full overflow-hidden" style={{ background: "#0a1520" }}>
                      <div className="absolute top-0 h-full opacity-20" 
                        style={{ left: `${(row.opt[0]/row.mx)*100}%`, width: `${((row.opt[1]-row.opt[0])/row.mx)*100}%`, background: row.c }} />
                      <div className="h-full rounded-full transition-all duration-500" 
                        style={{ width: `${Math.min(100, (row.v/row.mx)*100)}%`, background: row.c }} />
                    </div>
                  </div>
                ))}

                <div className="flex gap-2 mt-3">
                  <BtnPrimary label="📄 تقرير مفصل" />
                  <BtnGhost label="🤖 استشارة AI" />
                </div>
              </div>
            </Card>
          )}

          {/* Index description */}
          <Card className="p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded flex items-center justify-center text-lg"
                style={{ background: `${idxInfo.c}15`, color: idxInfo.c }}>
                ◈
              </div>
              <div>
                <div className="text-sm font-bold" style={{ color: JD.text }}>{idxInfo.lab}</div>
                <div className="text-[9px]" style={{ color: JD.textMuted }}>{idxInfo.cat}</div>
              </div>
            </div>
            <div className="text-[10px] leading-relaxed" style={{ color: JD.textSub }}>{idxInfo.desc}</div>
            <div className="mt-2 flex gap-1.5 flex-wrap">
              <Pill label={idxInfo.cat === "SAR رادار" ? "Sentinel-1" : "Sentinel-2"} size="xs" />
              {idxInfo.id === "hybrid" && <Pill label="الافتراضي" color={JD.yellow} size="xs" />}
            </div>
          </Card>

          {/* All fields summary */}
          <Card>
            <div className="px-3 py-2.5 border-b text-[10px] font-bold" style={{ color: JD.text, borderColor: JD.border }}>
              ملخص الحقول — {idxInfo.lab}
            </div>
            <div className="p-2 space-y-1">
              {FIELDS.map(f => {
                const color = getFieldBorderColor(selIdx, f.ndvi);
                return (
                  <div key={f.id} onClick={() => setSelField(f)}
                    className="flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer transition-colors"
                    style={{ background: selField?.id === f.id ? "rgba(54,124,43,0.08)" : "transparent" }}>
                    <div className="w-2.5 h-2.5 rounded-sm flex-shrink-0" style={{ background: color }} />
                    <div className="flex-1 min-w-0">
                      <div className="text-[10px] font-bold truncate" style={{ color: JD.text }}>{f.n}</div>
                    </div>
                    <div className="text-[10px] font-black tabular-nums" style={{ color }}>
                      {selIdx === "hybrid" ? (
                        f.ndvi >= 0.7 ? "🟢" : f.ndvi >= 0.5 ? "🟠" : f.ndvi >= 0.3 ? "🟣" : "🔴"
                      ) : (
                        f.ndvi
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* SAR fallback notice */}
          <div className="rounded-lg p-3" style={{ background: "rgba(56,189,248,0.05)", border: "1px solid rgba(56,189,248,0.15)" }}>
            <div className="text-[10px] font-bold mb-1" style={{ color: JD.blue }}>📡 SAR تلقائي</div>
            <div className="text-[9px] leading-relaxed" style={{ color: JD.textMuted }}>
              عند الغيوم ≥ 60%، يتحول تلقائياً إلى Sentinel-1 (RVI + RSM).
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
function IndicesPanel() {
const [active,setActive]=useState(“hybrid”);
const [cat,setCat]=useState(“الكل”);
const cats=[“الكل”,…new Set(ALL_INDICES.map(i=>i.cat))];
const filtered=cat===“الكل”?ALL_INDICES:ALL_INDICES.filter(i=>i.cat===cat);
const sel=ALL_INDICES.find(i=>i.id===active)||ALL_INDICES[0];

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-2.5 flex gap-2 items-center flex-wrap">
<TabStrip options={cats} active={cat} onChange={setCat}/>
<div className=“mr-auto rounded px-3 py-1.5 text-[9px]” style={{background:“rgba(56,189,248,.06)”,border:“1px solid rgba(56,189,248,.15)”,color:JD.blue}}>
📡 عند الغيوم: RVI + RSM تلقائياً من Sentinel-1
</div>
</div>
</Card>

```
  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2.5">
    {filtered.map(idx=>(
      <Card key={idx.id}
        className="p-3 transition-all"
        style={{
          borderRight:`2px solid ${active===idx.id?idx.c:"transparent"}`,
          background:active===idx.id?`${idx.c}08`:JD.surface,
        }}
        onClick={()=>setActive(idx.id)}>
        <div className="flex justify-between items-start mb-2">
          <div>
            <div className="font-black text-sm" style={{color:idx.c}}>{idx.lab}</div>
            <Pill label={idx.cat} color={idx.c} size="xs"/>
          </div>
          {active===idx.id && <span className="text-[10px]" style={{color:idx.c}}>◆</span>}
        </div>
        <div className="text-[9px] leading-relaxed mt-2" style={{color:JD.textMuted}}>{idx.desc}</div>
      </Card>
    ))}
  </div>

  {sel && (
    <div className="rounded-lg p-4 flex gap-4 items-start" style={{background:`${sel.c}06`,border:`1px solid ${sel.c}20`}}>
      <div className="font-black text-4xl leading-none min-w-[80px] text-center" style={{color:sel.c}}>{sel.lab}</div>
      <div className="flex-1">
        <div className="text-sm font-bold mb-2" style={{color:JD.text}}>{sel.desc}</div>
        <div className="flex gap-2 flex-wrap mb-2">
          <Pill label={`الفئة: ${sel.cat}`} color={sel.c}/>
          <Pill label={sel.cat==="SAR رادار"?"Sentinel-1":"Sentinel-2"}/>
          {sel.id==="hybrid" && <Pill label="الافتراضي للمزارع" color={JD.yellow}/>}
        </div>
      </div>
    </div>
  )}
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
TIME SERIES
═══════════════════════════════════════════════════════════════ */
function TimeSeries({field}:{field:Field}) {
const [period,setPeriod]=useState(“شهر”);
const series=[
{label:“NDVI”,data:[.42,.47,.51,.56,.53,.58,.61,.66,.72,.75,.78,.74,.70,.73,.77],color:”#22C55E”},
{label:“NDWI”,data:[.38,.41,.44,.43,.47,.51,.55,.57,.61,.59,.62,.58,.55,.60,.63],color:”#38BDF8”},
{label:“NDMI”,data:[.28,.31,.35,.40,.38,.41,.43,.44,.44,.42,.40,.41,.38,.43,.46],color:”#F59E0B”},
];
const dates=[“1/2”,“3/2”,“5/2”,“7/2”,“9/2”,“11/2”,“13/2”,“15/2”,“17/2”,“19/2”,“21/2”,“23/2”,“25/2”,“27/2”,“الآن”];

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-2.5 flex gap-2 items-center flex-wrap">
<span className="text-sm font-bold" style={{color:JD.text}}>السلاسل الزمنية</span>
<TabStrip options={[“أسبوع”,“شهر”,“3 أشهر”,“موسم”]} active={period} onChange={setPeriod}/>
<span className="text-[10px]" style={{color:JD.textMuted}}>◎ {field.n}</span>
<div className="mr-auto flex gap-2">
<BtnGhost label="تصدير CSV"/><BtnGhost label="Timelapse"/><BtnPrimary label="مقارنة جانبية ⊟"/>
</div>
</div>
</Card>

```
  <Card className="p-4">
    <div className="flex justify-between items-center mb-3">
      <div>
        <div className="text-sm font-bold" style={{color:JD.text}}>NDVI · NDWI · NDMI</div>
        <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>كل نقطة = مرور قمر صناعي</div>
      </div>
      <div className="flex gap-3">
        {series.map(s=>(
          <div key={s.label} className="flex items-center gap-1.5 text-[10px]" style={{color:s.color}}>
            <div className="w-4 h-0.5 rounded-sm" style={{background:s.color}}/>{s.label}
          </div>
        ))}
      </div>
    </div>
    <MultiLine series={series} h={140}/>
    <div className="flex justify-between text-[8px] mt-1.5 px-1" style={{color:JD.textMuted}}>
      {dates.filter((_,i)=>i%4===0||i===dates.length-1).map(d=><span key={d}>{d}</span>)}
    </div>
  </Card>

  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
    {series.map(s=>(
      <Card key={s.label} className="p-4" style={{borderRight:`2px solid ${s.color}`}}>
        <div className="flex justify-between items-start mb-3">
          <div>
            <div className="font-black" style={{color:s.color}}>{s.label}</div>
            <div className="text-[9px]" style={{color:JD.textMuted}}>آخر قراءة</div>
          </div>
          <div className="text-left">
            <div className="text-xl font-black tabular-nums leading-none" style={{color:s.color}}>
              {Math.round(s.data[s.data.length-1]*100)}<span className="text-[9px]" style={{color:JD.textMuted}}>%</span>
            </div>
            <div className="text-[9px]" style={{color:s.data[s.data.length-1]>s.data[s.data.length-2]?JD.greenGlow:JD.red}}>
              {s.data[s.data.length-1]>s.data[s.data.length-2]?"↑":"↓"}
              {Math.abs(Math.round((s.data[s.data.length-1]-s.data[s.data.length-2])*100))}%
            </div>
          </div>
        </div>
        <Spark data={s.data} color={s.color} h={60}/>
        <div className="flex justify-between text-[9px] mt-1.5" style={{color:JD.textMuted}}>
          <span>أدنى: <span style={{color:s.color}}>{Math.round(Math.min(...s.data)*100)}%</span></span>
          <span>أقصى: <span style={{color:s.color}}>{Math.round(Math.max(...s.data)*100)}%</span></span>
        </div>
      </Card>
    ))}
  </div>

  <div className="rounded-lg p-3 flex gap-3 items-center" style={{background:"rgba(56,189,248,.04)",border:"1px solid rgba(56,189,248,.15)"}}>
    <span className="text-xl">📡</span>
    <div>
      <div className="text-[10px] font-bold mb-0.5" style={{color:JD.blue}}>SAR تلقائي — 3–5 فبراير (غيوم 80%)</div>
      <div className="text-[9px] leading-relaxed" style={{color:JD.textMuted}}>
        النقاط في هذه الفترة من Sentinel-1 (RVI+RSM). جودة البيانات محفوظة.
      </div>
    </div>
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
REPORTS
═══════════════════════════════════════════════════════════════ */
function Reports({field}:{field:Field}) {
const [selDate,setSelDate]=useState(REPORT_DATES[0]);
const dirs=field.dir||[];

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-3 flex justify-between items-center">
<div>
<div className="text-sm font-bold" style={{color:JD.text}}>{field.n} — {selDate}</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>4 صفحات · تحديث كل 5 أيام</div>
</div>
<div className="flex gap-2">
<select className="px-2.5 py-1.5 rounded text-[10px] border outline-none cursor-pointer"
style={{background:JD.panel,color:JD.textSub,borderColor:JD.border}}>
<option>العربية</option><option>English</option>
</select>
<BtnGhost label="⬇ PDF"/><BtnPrimary label="📱 WhatsApp"/>
</div>
</div>
</Card>

```
  <div className="grid grid-cols-1 xl:grid-cols-[220px_1fr] gap-3">
    {/* Date list */}
    <Card>
      <SectionHeader title="تواريخ الزيارات" sub="كل 3–5 أيام"/>
      <div className="overflow-y-auto" style={{maxHeight:400,scrollbarWidth:"none"}}>
        {REPORT_DATES.map((d,i)=>(
          <div key={d} onClick={()=>setSelDate(d)}
            className="px-3 py-2.5 cursor-pointer border-b transition-all"
            style={{
              borderColor:JD.border,
              background:selDate===d?"rgba(54,124,43,.06)":"transparent",
              borderRight:selDate===d?`2px solid ${JD.greenGlow}`:"2px solid transparent",
            }}>
            <div className="flex justify-between items-center">
              <span className="text-[10px] font-bold tabular-nums" style={{color:selDate===d?JD.text:JD.textSub}}>{d}</span>
              {i===0 && <Pill label="أحدث" size="xs"/>}
            </div>
            <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>NDVI: .{72+i}2 · سحاب: {(i*3)%22}%</div>
          </div>
        ))}
      </div>
    </Card>

    {/* Report content */}
    <div className="flex flex-col gap-3">
      <Card className="p-4">
        <div className="text-sm font-bold mb-0.5" style={{color:JD.text}}>الصفحة 2 — خريطة الاتجاهات التسعة</div>
        <div className="text-[9px] mb-4" style={{color:JD.greenGlow}}>◆ الأهم للمزارع</div>
        <div className="flex gap-5 items-start">
          <DirGrid alerts={dirs}/>
          <div className="flex-1">
            {dirs.length>0?(
              <>
                <div className="rounded-md p-3 mb-2" style={{background:"rgba(239,68,68,.06)",border:"1px solid rgba(239,68,68,.18)"}}>
                  <div className="text-[10px] font-bold mb-1" style={{color:JD.red}}>❶ فحص المحصول مطلوب في:</div>
                  <div className="text-[10px]" style={{color:JD.textSub}}>
                    <strong>{dirs.map(d=>DIR_CELLS.find(c=>c.id===d)?.ar).join(" · ")}</strong>
                    <br/>إجهاد مائي · آفات · مرض · تغذية ناقصة
                  </div>
                </div>
                <div className="rounded-md p-3" style={{background:"rgba(139,92,246,.06)",border:"1px solid rgba(139,92,246,.18)"}}>
                  <div className="text-[10px] font-bold mb-1" style={{color:JD.purple}}>❷ فحص نظام الري في:</div>
                  <div className="text-[10px]" style={{color:JD.textSub}}>
                    <strong>{dirs.map(d=>DIR_CELLS.find(c=>c.id===d)?.ar).join(" · ")}</strong>
                    <br/>تسرب · انسداد · توزيع غير متساوٍ
                  </div>
                </div>
              </>
            ):(
              <div className="rounded-md p-3" style={{background:"rgba(16,185,129,.06)",border:"1px solid rgba(16,185,129,.18)"}}>
                <div className="text-[10px] font-bold mb-1" style={{color:JD.greenGlow}}>✓ كل الاتجاهات بحالة جيدة</div>
                <div className="text-[9px]" style={{color:JD.textSub}}>صحة المحصول ممتازة · الري منتظم</div>
              </div>
            )}
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Card className="p-4">
          <div className="text-xs font-bold mb-3" style={{color:JD.text}}>ملخص المؤشرات</div>
          {[
            {n:"NDVI صحة المحصول",v:`${Math.round(field.ndvi*100)}%`,c:stc(field.st)},
            {n:"رطوبة التربة",v:`${field.moist}%`,c:field.moist<35?JD.red:JD.greenGlow},
            {n:"EC الملوحة",v:`${field.ec} dS/m`,c:field.ec>2?JD.red:JD.greenGlow},
            {n:"الارتفاع",v:`${field.elev}م`,c:JD.textSub},
            {n:"المحصول",v:field.crop,c:JD.text},
            {n:"SAR متاح",v:"Sentinel-1",c:JD.blue},
          ].map((row,i)=>(
            <div key={i} className="flex justify-between py-2" style={{borderBottom:i<5?`1px solid ${JD.border}`:"none"}}>
              <span className="text-[10px]" style={{color:JD.textMuted}}>{row.n}</span>
              <span className="text-[10px] font-bold" style={{color:row.c}}>{row.v}</span>
            </div>
          ))}
        </Card>

        <Card className="p-4">
          <div className="text-xs font-bold mb-3" style={{color:JD.text}}>صفحات التقرير الأربع</div>
          {[
            {pg:"1",t:"معلومات الحقل",s:"المالك · المساحة · التاريخ",accent:false},
            {pg:"2",t:"خريطة 9 اتجاهات",s:"التوصيات الرئيسية",accent:true},
            {pg:"3",t:"المؤشرات التفصيلية",s:"NDVI · NDWI · SOC · ET",accent:false},
            {pg:"4",t:"بيانات الطقس",s:"يوم الزيارة · التبخر · GDD",accent:false},
          ].map(p=>(
            <div key={p.pg} className="flex gap-3 items-center py-2" style={{borderBottom:p.pg!=="4"?`1px solid ${JD.border}`:"none"}}>
              <div className="w-6 h-6 rounded flex items-center justify-center text-[10px] font-black flex-shrink-0"
                style={{background:p.accent?`${JD.yellow}18`:"#0a1520",color:p.accent?JD.yellow:JD.textMuted}}>{p.pg}</div>
              <div>
                <div className="text-[10px] font-bold" style={{color:JD.text}}>{p.t}</div>
                <div className="text-[9px]" style={{color:JD.textMuted}}>{p.s}</div>
              </div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
WEATHER
═══════════════════════════════════════════════════════════════ */
function Weather() {
return (
<div className="flex flex-col gap-3">
<Card className="p-4">
<div className="flex justify-between items-start mb-4">
<div>
<div className="text-sm font-bold" style={{color:JD.text}}>الطقس المحلي</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>الرياض · تحديث كل 3 ساعات</div>
</div>
<div className="text-left">
<div className="text-3xl font-black tabular-nums leading-none" style={{color:JD.orange}}>26°</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>⛅ غائم جزئياً</div>
</div>
</div>

```
    <div className="grid grid-cols-4 gap-2 mb-4">
      {[{l:"الرياح",v:"2.4 م/ث",i:"💨"},{l:"الرطوبة",v:"41%",i:"💧"},{l:"الضغط",v:"1013 hPa",i:"📊"},{l:"UV",v:"6 عالي",i:"☀"}].map(m=>(
        <div key={m.l} className="rounded-md p-2.5 text-center" style={{background:"#0a1520"}}>
          <div className="text-base mb-1">{m.i}</div>
          <div className="text-[10px] font-bold" style={{color:JD.text}}>{m.v}</div>
          <div className="text-[9px]" style={{color:JD.textMuted}}>{m.l}</div>
        </div>
      ))}
    </div>

    <div className="h-px mb-3" style={{background:JD.border}}/>
    <div className="text-[10px] font-bold mb-2" style={{color:JD.text}}>توقعات 7 أيام</div>
    <div className="grid grid-cols-7 gap-1.5">
      {WX7.map((d,i)=>(
        <div key={i} className="rounded-md p-2 text-center"
          style={{background:i===0?"rgba(245,158,11,.07)":"#0a1520",border:i===0?"1px solid rgba(245,158,11,.18)":"none"}}>
          <div className="text-[9px] mb-1" style={{color:JD.textMuted}}>{d.d}</div>
          <div className="text-base mb-1">{d.ic}</div>
          <div className="text-[10px] font-bold tabular-nums" style={{color:i===0?JD.orange:JD.text}}>{d.hi}°</div>
          <div className="text-[8px] tabular-nums" style={{color:JD.textMuted}}>{d.lo}°</div>
          <div className="text-[8px] mt-0.5" style={{color:d.prob>50?JD.red:JD.textMuted}}>{d.prob}%</div>
        </div>
      ))}
    </div>
  </Card>

  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    <Card className="p-4">
      <div className="text-xs font-bold mb-3" style={{color:JD.text}}>GDD — درجات النمو المتراكمة</div>
      <div className="flex items-baseline gap-2 mb-2">
        <div className="text-2xl font-black tabular-nums" style={{color:JD.orange}}>1,650</div>
        <div className="text-[9px]" style={{color:JD.textMuted}}>/ 2,100 هدف الموسم</div>
      </div>
      <div className="h-2 rounded-full overflow-hidden mb-3" style={{background:"#0a1520"}}>
        <div className="h-full rounded-full" style={{width:"78.6%",background:`linear-gradient(90deg,${JD.orange},${JD.greenGlow})`}}/>
      </div>
      <div className="grid grid-cols-4 gap-1.5">
        {[{v:"200",l:"إنبات"},{v:"600",l:"تفريع"},{v:"1,200",l:"إزهار ←",h:true},{v:"2,100",l:"نضج"}].map(e=>(
          <div key={e.l} className="text-center rounded p-1.5"
            style={{background:e.h?"rgba(245,158,11,.08)":"#0a1520",border:e.h?"1px solid rgba(245,158,11,.2)":"none"}}>
            <div className="text-[10px] font-bold" style={{color:e.h?JD.orange:JD.text}}>{e.v}</div>
            <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>{e.l}</div>
          </div>
        ))}
      </div>
    </Card>

    <Card className="p-4">
      <div className="text-xs font-bold mb-3" style={{color:JD.text}}>ET — التبخر النتحي</div>
      <div className="flex justify-between items-center mb-2">
        <span className="text-[10px]" style={{color:JD.textMuted}}>القيمة اليومية</span>
        <span className="text-lg font-black tabular-nums" style={{color:JD.blue}}>4.2 mm</span>
      </div>
      <RangeBar v={42} mx={80} opt={[20,60]} color={JD.blue}/>
      <div className="grid grid-cols-3 gap-2 mt-3">
        {[{l:"الأسبوع",v:"28.5 mm"},{l:"الشهر",v:"112 mm"},{l:"الموسم",v:"340 mm"}].map(e=>(
          <div key={e.l} className="text-center rounded p-2" style={{background:"#0a1520"}}>
            <div className="text-[10px] font-bold" style={{color:JD.text}}>{e.v}</div>
            <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>{e.l}</div>
          </div>
        ))}
      </div>
    </Card>
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
SENSORS
═══════════════════════════════════════════════════════════════ */
function Sensors() {
return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-3 flex justify-between items-center">
<div>
<div className="text-sm font-bold" style={{color:JD.text}}>المستشعرات IoT</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>7 مستشعرات نشطة · تحديث كل 5 دقائق</div>
</div>
<div className="flex gap-2">
<BtnGhost label="⬇ CSV"/><BtnPrimary label="+ إضافة مستشعر"/>
</div>
</div>
</Card>

```
  <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
    {SENSORS.map(s=>{
      const ok=s.v>=s.opt[0]&&s.v<=s.opt[1];
      const col=ok?JD.greenGlow:s.v<s.opt[0]?JD.blue:JD.red;
      return (
        <Card key={s.id} style={{borderTop:`2px solid ${col}`}}>
          <div className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="text-xs font-bold" style={{color:JD.text}}>{s.n}</div>
                <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{s.field} · عمق {s.dep}</div>
              </div>
              <div className="text-left">
                <div className="text-xl font-black tabular-nums leading-none" style={{color:col}}>
                  {s.v}<span className="text-[9px] font-normal" style={{color:JD.textMuted}}> {s.u}</span>
                </div>
                <div className="text-[9px] mt-0.5" style={{color:ok?JD.greenGlow:JD.red}}>
                  {ok?"✓ مثالي":"⚠ خارج المدى"}
                </div>
              </div>
            </div>
            <RangeBar v={s.v} mx={s.mx} opt={s.opt} color={col}/>
            <div className="flex justify-between items-center mt-3">
              <Battery pct={s.bat}/>
              <Signal n={s.sig}/>
              <span className="text-[9px]" style={{color:JD.textMuted}}>منذ {s.last}</span>
            </div>
          </div>
        </Card>
      );
    })}
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
AI CHAT
═══════════════════════════════════════════════════════════════ */
function AIChat() {
const [msgs,setMsgs]=useState(AI_MESSAGES);
const [inp,setInp]=useState(””);
const [thinking,setThinking]=useState(false);
const bottomRef=useRef<HTMLDivElement>(null);

useEffect(()=>{bottomRef.current?.scrollIntoView({behavior:“smooth”})},[msgs]);

const send=()=>{
if(!inp.trim()||thinking) return;
const q=inp;setInp(””);setThinking(true);
setMsgs(m=>[…m,{from:“user”,text:q}]);
setTimeout(()=>{
setMsgs(m=>[…m,{from:“ai”,text:“بناءً على بيانات حقولك الحالية، أنصح بمراجعة مستشعر EC في حوض الغرب. هل تريد تقريراً مفصلاً؟”}]);
setThinking(false);
},1400);
};

return (
<div className="flex flex-col gap-3 h-full">
<Card>
<div className="p-3">
<div className="text-sm font-bold" style={{color:JD.text}}>المستشار الذكي SAHOOL AI</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>تحليل في الوقت الحقيقي · مدعوم بـ GPT-4</div>
</div>
</Card>

```
  <Card className="flex-1 flex flex-col min-h-0">
    <div className="flex-1 p-4 overflow-y-auto space-y-3" style={{minHeight:360,scrollbarWidth:"none"}}>
      {msgs.map((m,i)=>(
        <div key={i} className={`flex ${m.from==="user"?"justify-start":"justify-end"}`}>
          <div className="max-w-[78%] rounded-lg px-3.5 py-2.5 text-[11px] leading-relaxed whitespace-pre-wrap"
            style={{
              background:m.from==="user"?"rgba(56,189,248,.1)":"rgba(54,124,43,.12)",
              border:`1px solid ${m.from==="user"?"rgba(56,189,248,.2)":"rgba(54,124,43,.25)"}`,
              color:JD.text,
              borderRadius:m.from==="user"?"12px 12px 12px 2px":"12px 12px 2px 12px",
            }}>
            {m.text}
          </div>
        </div>
      ))}
      {thinking && (
        <div className="flex justify-end">
          <div className="rounded-lg px-3.5 py-2.5" style={{background:"rgba(54,124,43,.08)",border:"1px solid rgba(54,124,43,.2)"}}>
            <div className="flex gap-1.5 items-center">
              {[0,1,2].map(i=>(
                <div key={i} className="w-1.5 h-1.5 rounded-full" style={{background:JD.greenGlow,animation:`bounce .8s ${i*.15}s infinite`}}/>
              ))}
            </div>
          </div>
        </div>
      )}
      <div ref={bottomRef}/>
    </div>

    <div className="p-3 border-t flex gap-2" style={{borderColor:JD.border}}>
      <input value={inp} onChange={e=>setInp(e.target.value)} onKeyDown={e=>e.key==="Enter"&&send()}
        placeholder="اكتب سؤالك هنا..."
        className="flex-1 px-3.5 py-2 rounded-lg text-[11px] outline-none border"
        style={{background:"#0a1520",color:JD.text,borderColor:JD.border}}/>
      <BtnPrimary label="إرسال ↑" onClick={send}/>
    </div>
  </Card>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
TASKS
═══════════════════════════════════════════════════════════════ */
function TasksScreen() {
const [tasks,setTasks]=useState(TASKS);
const [filter,setFilter]=useState(“الكل”);
const filtered=filter===“الكل”?tasks:tasks.filter(t=>t.due===filter);
const toggle=(id:number)=>setTasks(tasks.map(t=>t.id===id?{…t,done:!t.done}:t));

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-2.5 flex gap-2 items-center flex-wrap">
<span className="text-sm font-bold" style={{color:JD.text}}>إدارة المهام</span>
<TabStrip options={[“الكل”,“اليوم”,“غداً”,“دوري”]} active={filter} onChange={setFilter}/>
<div className="mr-auto"><BtnPrimary label="+ مهمة جديدة"/></div>
</div>
</Card>

```
  <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
    {filtered.map(t=>(
      <Card key={t.id} className="p-3.5 flex gap-3 items-start" style={{opacity:t.done?.75:1}}>
        <button onClick={()=>toggle(t.id)}
          className="mt-0.5 w-4.5 h-4.5 rounded-sm border-2 flex items-center justify-center flex-shrink-0 cursor-pointer transition-all"
          style={{
            width:18,height:18,
            borderColor:t.done?JD.greenGlow:JD.border,
            background:t.done?`${JD.greenGlow}15`:"transparent",
          }}>
          {t.done&&<span className="text-[9px]" style={{color:JD.greenGlow}}>✓</span>}
        </button>
        <div className="flex-1 min-w-0">
          <div className="text-[11px] font-bold" style={{color:t.done?JD.textMuted:JD.text,textDecoration:t.done?"line-through":"none"}}>{t.t}</div>
          <div className="text-[9px] mt-1 flex gap-1.5 flex-wrap" style={{color:JD.textMuted}}>
            <span>{t.f}</span><span>·</span>
            <span style={{color:t.p==="h"?JD.red:t.p==="m"?JD.orange:JD.textMuted}}>
              {t.p==="h"?"🔴 عالي":t.p==="m"?"🟡 متوسط":"⚪ منخفض"}
            </span>
            <span>·</span><span>{t.tm}</span><span>·</span><span>{t.a}</span>
          </div>
        </div>
        <Pill label={t.due} color={t.due==="اليوم"?JD.orange:t.due==="غداً"?JD.blue:JD.textMuted} size="xs"/>
      </Card>
    ))}
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
TEAM
═══════════════════════════════════════════════════════════════ */
function TeamScreen() {
return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-3 flex justify-between items-center">
<div>
<div className="text-sm font-bold" style={{color:JD.text}}>الفريق</div>
<div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>4 أعضاء · 3 متصلون الآن</div>
</div>
<BtnPrimary label="+ دعوة عضو"/>
</div>
</Card>

```
  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {TEAM.map(m=>(
      <Card key={m.id} className="p-4 flex gap-3 items-center">
        <div className="relative flex-shrink-0">
          <div className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-black"
            style={{background:m.st==="on"?`${JD.greenGlow}15`:"#0a1520",color:m.st==="on"?JD.greenGlow:JD.textMuted,border:`2px solid ${m.st==="on"?`${JD.greenGlow}30`:JD.border}`}}>
            {m.av}
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2"
            style={{background:m.st==="on"?JD.greenGlow:JD.textMuted,borderColor:JD.surface}}/>
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-bold" style={{color:JD.text}}>{m.n}</div>
          <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{m.fields} حقول · منذ {m.join}</div>
          <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{m.email}</div>
        </div>
        <Pill
          label={m.role==="admin"?"مسؤول":m.role==="editor"?"محرر":"مشاهد"}
          color={m.role==="admin"?JD.yellow:m.role==="editor"?JD.greenGlow:JD.textMuted}
        />
      </Card>
    ))}
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
SCOUTING
═══════════════════════════════════════════════════════════════ */
function ScoutingScreen({fields}:{fields:Field[]}) {
const [selField,setSelField]=useState(“الكل”);
const filtered=selField===“الكل”?SCOUT_NOTES:SCOUT_NOTES.filter(s=>s.field===selField);
const typeColor=(t:string)=>t===“تحذير”?JD.red:t===“جيد”?JD.greenGlow:JD.textSub;

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-2.5 flex gap-2 items-center flex-wrap">
<span className="text-sm font-bold" style={{color:JD.text}}>المسح الميداني</span>
<TabStrip options={[“الكل”,…fields.map(f=>f.n)]} active={selField} onChange={setSelField}/>
<div className="mr-auto"><BtnPrimary label="+ ملاحظة جديدة"/></div>
</div>
</Card>

```
  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
    {filtered.map(note=>(
      <Card key={note.id} className="p-4" style={{borderRight:`2px solid ${typeColor(note.type)}`}}>
        <div className="flex justify-between items-start mb-2">
          <div className="flex items-center gap-2">
            <Pill label={note.field} size="xs"/>
            <span className="text-[9px]" style={{color:JD.textMuted}}>{note.date}</span>
          </div>
          <Pill label={note.type} color={typeColor(note.type)} size="xs"/>
        </div>
        <div className="text-[11px] leading-relaxed mb-2" style={{color:JD.textSub}}>{note.note}</div>
        <div className="flex justify-between items-center">
          <span className="text-[9px]" style={{color:JD.textMuted}}>بواسطة: {note.author}</span>
          {note.img && (
            <div className="flex gap-1">
              <div className="w-7 h-7 rounded" style={{background:"#2d6b24"}}/>
              <div className="w-7 h-7 rounded" style={{background:"#367C2B"}}/>
            </div>
          )}
        </div>
      </Card>
    ))}
  </div>

  <Card className="p-4">
    <div className="text-xs font-bold mb-3" style={{color:JD.text}}>إحصائيات</div>
    <div className="grid grid-cols-4 gap-3">
      {[
        {l:"إجمالي",v:SCOUT_NOTES.length,c:JD.greenGlow},
        {l:"تحذيرات",v:SCOUT_NOTES.filter(n=>n.type==="تحذير").length,c:JD.red},
        {l:"جيدة",v:SCOUT_NOTES.filter(n=>n.type==="جيد").length,c:JD.greenGlow},
        {l:"بصور",v:SCOUT_NOTES.filter(n=>n.img).length,c:JD.blue},
      ].map(s=>(
        <div key={s.l} className="text-center rounded-md p-3" style={{background:"#0a1520"}}>
          <div className="text-lg font-black" style={{color:s.c}}>{s.v}</div>
          <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{s.l}</div>
        </div>
      ))}
    </div>
  </Card>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
VRA
═══════════════════════════════════════════════════════════════ */
function VRAScreen() {
const [type,setType]=useState(“سماد N”);
const zones=VRA_ZONES.filter(z=>z.type===type);

return (
<div className="flex flex-col gap-3">
<Card>
<div className="p-2.5 flex gap-2 items-center flex-wrap">
<span className="text-sm font-bold" style={{color:JD.text}}>خرائط الزراعة المتغيرة (VRA)</span>
<TabStrip options={[“سماد N”,“سماد P”,“بذور”,“مبيدات”]} active={type} onChange={setType}/>
<div className="mr-auto flex gap-2">
<BtnGhost label="⬇ Shapefile"/><BtnPrimary label="+ خريطة جديدة"/>
</div>
</div>
</Card>

```
  <div className="grid grid-cols-1 xl:grid-cols-[1fr_260px] gap-3">
    <Card className="p-4">
      <div className="text-xs font-bold mb-3" style={{color:JD.text}}>خريطة المناطق — {type}</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {["حقل الشمال","الوادي الأوسط"].map(f=>{
          const fz=zones.filter(z=>z.field===f);
          return (
            <div key={f} className="rounded-md p-3" style={{background:"#0a1520",border:`1px solid ${JD.border}`}}>
              <div className="text-[11px] font-bold mb-2.5" style={{color:JD.text}}>{f}</div>
              <div className="flex gap-2">
                {fz.map(z=>(
                  <div key={z.id} className="flex-1 rounded-md p-2 text-center" style={{background:`${z.color}10`,border:`1px solid ${z.color}30`}}>
                    <div className="text-[9px] font-bold mb-1" style={{color:z.color}}>{z.zone}</div>
                    <div className="text-xl font-black tabular-nums" style={{color:z.color}}>{z.rate}</div>
                    <div className="text-[8px]" style={{color:JD.textMuted}}>{z.unit}</div>
                    <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>{z.area} هـ</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 rounded-md p-2.5 flex gap-4" style={{background:"#0a1520"}}>
        {[{c:"#EF4444",l:"منخفضة — جرعة عالية"},{c:"#F59E0B",l:"متوسطة — جرعة متوسطة"},{c:"#10B981",l:"عالية — جرعة منخفضة"}].map(lv=>(
          <div key={lv.l} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-sm" style={{background:lv.c}}/>
            <span className="text-[9px]" style={{color:JD.textSub}}>{lv.l}</span>
          </div>
        ))}
      </div>
    </Card>

    <div className="flex flex-col gap-3">
      <Card className="p-4">
        <div className="text-xs font-bold mb-3" style={{color:JD.text}}>ملخص الجرعات</div>
        {[{l:"إجمالي المساحة",v:"6.2 هـ"},{l:"متوسط الجرعة",v:"113 كغ/هـ"},{l:"الكمية الإجمالية",v:"700 كغ"},{l:"التوفير المتوقع",v:"12%"}].map(s=>(
          <div key={s.l} className="flex justify-between py-2" style={{borderBottom:`1px solid ${JD.border}`}}>
            <span className="text-[10px]" style={{color:JD.textMuted}}>{s.l}</span>
            <span className="text-[10px] font-black tabular-nums" style={{color:JD.text}}>{s.v}</span>
          </div>
        ))}
      </Card>

      <Card className="p-4">
        <div className="text-xs font-bold mb-2" style={{color:JD.text}}>متوافق مع</div>
        <div className="flex flex-wrap gap-1.5">
          {["John Deere","Trimble","ISO-XML","Shapefile","KML"].map(b=>(
            <Pill key={b} label={b} size="xs"/>
          ))}
        </div>
      </Card>
    </div>
  </div>
</div>
```

);
}

/* ═══════════════════════════════════════════════════════════════
TRACE
═══════════════════════════════════════════════════════════════ */
function TraceScreen() {
  return (
    <div className="flex flex-col gap-3">
      <Card>
        <div className="p-3 flex justify-between items-center">
          <div>
            <div className="text-sm font-bold" style={{color:JD.text}}>تتبع المنتج — Blockchain</div>
            <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>ID: SAH-2026-001 · حقل الشمال · قمح</div>
          </div>
          <Pill label="مفعّل" color={JD.greenGlow}/>
        </div>
      </Card>

      <div className="relative pr-8">
        {/* Timeline line */}
        <div className="absolute top-0 bottom-0 right-3 w-0.5 rounded-full" style={{background:`linear-gradient(to bottom,${JD.greenGlow},${JD.yellow}50)`}}/>
        <div className="space-y-3">
          {TRACE_STEPS.map(step=>{
            const isDone = step.status === "done";
            return (
              <div key={step.step} className="relative flex gap-4">
                {/* Node */}
                <div className="absolute -right-[22px] w-4 h-4 rounded-full border-2 z-10 flex items-center justify-center"
                  style={{background:isDone?JD.greenGlow:JD.surface,borderColor:isDone?JD.greenGlow:JD.border}}>
                  {isDone && <span className="text-[7px] font-black" style={{color:"#000"}}>✓</span>}
                </div>
                <Card className="flex-1 p-3.5" style={{opacity:isDone?1:.55}}>
                  <div className="flex justify-between items-center mb-1.5">
                    <div className="text-[11px] font-bold" style={{color:JD.text}}>{step.step}. {step.title}</div>
                    <Pill label={isDone?"مكتمل":"معلق"} color={isDone?JD.greenGlow:JD.textMuted} size="xs"/>
                  </div>
                  <div className="flex gap-3 flex-wrap text-[9px]" style={{color:JD.textMuted}}>
                    <span>📅 {step.date}</span><span>📍 {step.loc}</span>
                    <span>👤 {step.actor}</span><span>🏅 {step.cert}</span>
                  </div>
                </Card>
              </div>
            );
          })}
        </div>
      </div>

      <Card className="p-4">
        <div className="text-xs font-bold mb-3" style={{color:JD.text}}>الشهادات والمطابقة</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {["ISO 22000","Organic","Water-Smart","GlobalG.A.P"].map(cert=>{
            return (
              <div key={cert} className="rounded-md p-3 text-center" style={{background:"#0a1520",border:`1px solid ${JD.border}`}}>
                <div className="text-base mb-1">🏅</div>
                <div className="text-[10px] font-bold" style={{color:JD.text}}>{cert}</div>
                <div className="text-[9px] mt-0.5" style={{color:JD.greenGlow}}>✓ معتمد</div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  MACHINES
═══════════════════════════════════════════════════════════════ */
function MachinesScreen() {
  return (
    <div className="flex flex-col gap-3">
      <Card>
        <div className="p-3 flex justify-between items-center">
          <div>
            <div className="text-sm font-bold" style={{color:JD.text}}>المعدات والآلات</div>
            <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>4 آلات · 3 نشطة · 1 تحتاج صيانة</div>
          </div>
          <BtnPrimary label="+ إضافة آلة"/>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {MACHINES.map(m=>{
          const borderColor = m.alert?JD.red:JD.greenGlow;
          return (
            <Card key={m.id} style={{borderTop:`2px solid ${borderColor}`}}>
              <div className="p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="text-sm font-bold" style={{color:JD.text}}>{m.n}</div>
                    <div className="text-[9px] mt-0.5" style={{color:JD.textMuted}}>{m.type} · {m.loc}</div>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full" style={{background:m.st==="on"?JD.greenGlow:JD.textMuted}}/>
                    <span className="text-[9px]" style={{color:m.st==="on"?JD.greenGlow:JD.textMuted}}>{m.st==="on"?"نشط":"متوقف"}</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 mb-3">
                  {[
                    {label:"الوقود",value:`${m.fuel}%`,color:m.fuel<30?JD.red:m.fuel<50?JD.orange:JD.greenGlow},
                    {label:"DEF",value:`${m.def}%`,color:m.def<15?JD.red:m.def<30?JD.orange:JD.greenGlow},
                    {label:"الساعات",value:`${m.hours}h`,color:JD.textSub},
                  ].map(s=>{
                    return (
                      <div key={s.label} className="text-center rounded p-1.5" style={{background:"#0a1520"}}>
                        <div className="text-sm font-black tabular-nums" style={{color:s.color}}>{s.value}</div>
                        <div className="text-[8px] mt-0.5" style={{color:JD.textMuted}}>{s.label}</div>
                      </div>
                    );
                  })}
                </div>

                {m.alert && (
                  <div className="rounded-md p-2 mb-2 text-[10px] font-bold" style={{background:"rgba(239,68,68,.06)",border:"1px solid rgba(239,68,68,.18)",color:JD.red}}>
                    ⚠ {m.alert}
                  </div>
                )}
                {m.next && <div className="text-[9px]" style={{color:JD.textMuted}}>الصيانة القادمة: {m.next}</div>}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════
  NEW: FIELD DRAWING TOOLS — Professional boundary definition
  Inspired by John Deere Operations Center & Cropwise draw tools
═══════════════════════════════════════════════════════════════ */

interface Point { x: number; y: number }
interface DrawnField {
  id: number;
  name: string;
  points: Point[];
  area: number;
  crop: string;
  color: string;
}

const DRAW_TOOLS = [
  { id: "polygon", label: "مضلع", icon: "⬡", desc: "رسم حدود الحقل بالنقر" },
  { id: "rectangle", label: "مستطيل", icon: "▭", desc: "سحب لرسم مستطيل" },
  { id: "circle", label: "دائرة", icon: "◯", desc: "سحب لرسم دائرة" },
  { id: "freehand", label: "حر", icon: "✎", desc: "رسم حر بالماوس" },
  { id: "edit", label: "تعديل", icon: "✐", desc: "تحريك النقاط" },
  { id: "measure", label: "قياس", icon: "📏", desc: "قياس المسافة" },
];

function DrawingToolsScreen({ fields }: { fields: Field[] }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [tool, setTool] = useState("polygon");
  const [isDrawing, setIsDrawing] = useState(false);
  const [points, setPoints] = useState<Point[]>([]);
  const [drawnFields, setDrawnFields] = useState<DrawnField[]>([
    { id: 101, name: "حقل تجريبي", points: [{x:150,y:120},{x:280,y:100},{x:300,y:220},{x:160,y:240}], area: 2.1, crop: "قمح", color: "#367C2B" },
    { id: 102, name: "حقل جديد", points: [{x:350,y:150},{x:480,y:140},{x:500,y:260},{x:360,y:270}], area: 1.8, crop: "ذرة", color: "#F59E0B" },
  ]);
  const [selectedField, setSelectedField] = useState<DrawnField | null>(null);
  const [fieldName, setFieldName] = useState("");
  const [fieldCrop, setFieldCrop] = useState("قمح");
  const [showGrid, setShowGrid] = useState(true);
  const [snapToGrid, setSnapToGrid] = useState(true);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [lastPan, setLastPan] = useState({ x: 0, y: 0 });

  // Canvas drawing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const w = canvas.width;
    const h = canvas.height;

    // Clear
    ctx.fillStyle = '#0a1520';
    ctx.fillRect(0, 0, w, h);

    // Grid
    if (showGrid) {
      ctx.strokeStyle = 'rgba(26,40,64,0.5)';
      ctx.lineWidth = 0.5;
      const gridSize = 20 * zoom;
      for (let x = (pan.x % gridSize); x < w; x += gridSize) {
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
      }
      for (let y = (pan.y % gridSize); y < h; y += gridSize) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }
    }

    // Satellite background simulation
    ctx.fillStyle = 'rgba(45,107,36,0.15)';
    ctx.fillRect(50, 50, w-100, h-100);

    // Draw existing fields
    drawnFields.forEach(df => {
      const isSel = selectedField?.id === df.id;
      ctx.beginPath();
      ctx.moveTo(df.points[0].x * zoom + pan.x, df.points[0].y * zoom + pan.y);
      df.points.forEach((p, i) => {
        if (i > 0) ctx.lineTo(p.x * zoom + pan.x, p.y * zoom + pan.y);
      });
      ctx.closePath();
      ctx.fillStyle = `${df.color}30`;
      ctx.fill();
      ctx.strokeStyle = isSel ? JD.yellow : df.color;
      ctx.lineWidth = isSel ? 2.5 : 1.5;
      ctx.setLineDash(isSel ? [5, 3] : []);
      ctx.stroke();
      ctx.setLineDash([]);

      // Label
      const cx = df.points.reduce((s, p) => s + p.x, 0) / df.points.length * zoom + pan.x;
      const cy = df.points.reduce((s, p) => s + p.y, 0) / df.points.length * zoom + pan.y;
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(df.name, cx, cy - 8);
      ctx.font = '9px sans-serif';
      ctx.fillStyle = JD.textMuted;
      ctx.fillText(`${df.area} هـ · ${df.crop}`, cx, cy + 6);

      // Vertex handles for selected field
      if (isSel) {
        df.points.forEach(p => {
          ctx.beginPath();
          ctx.arc(p.x * zoom + pan.x, p.y * zoom + pan.y, 5, 0, Math.PI * 2);
          ctx.fillStyle = JD.yellow;
          ctx.fill();
          ctx.strokeStyle = '#000';
          ctx.lineWidth = 1;
          ctx.stroke();
        });
      }
    });

    // Draw current points
    if (points.length > 0) {
      ctx.beginPath();
      ctx.moveTo(points[0].x * zoom + pan.x, points[0].y * zoom + pan.y);
      points.forEach((p, i) => {
        if (i > 0) ctx.lineTo(p.x * zoom + pan.x, p.y * zoom + pan.y);
      });
      if (isDrawing && points.length > 1) {
        ctx.lineTo(points[points.length - 1].x * zoom + pan.x, points[points.length - 1].y * zoom + pan.y);
      }
      ctx.strokeStyle = JD.greenGlow;
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 2]);
      ctx.stroke();
      ctx.setLineDash([]);

      // Points
      points.forEach(p => {
        ctx.beginPath();
        ctx.arc(p.x * zoom + pan.x, p.y * zoom + pan.y, 4, 0, Math.PI * 2);
        ctx.fillStyle = JD.greenGlow;
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      // Close hint
      if (points.length >= 3) {
        const first = points[0];
        ctx.beginPath();
        ctx.arc(first.x * zoom + pan.x, first.y * zoom + pan.y, 8, 0, Math.PI * 2);
        ctx.strokeStyle = JD.yellow;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([2, 2]);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }

    // Measurement line
    if (tool === "measure" && points.length === 2) {
      const p1 = points[0], p2 = points[1];
      const dist = Math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2) * 0.5; // scale factor
      const mx = (p1.x + p2.x) / 2 * zoom + pan.x;
      const my = (p1.y + p2.y) / 2 * zoom + pan.y;
      ctx.fillStyle = JD.yellow;
      ctx.font = 'bold 11px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${dist.toFixed(1)} م`, mx, my - 5);
    }

  }, [points, isDrawing, drawnFields, selectedField, showGrid, zoom, pan, tool]);

  const getCanvasPoint = (e: React.MouseEvent<HTMLCanvasElement>): Point => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    let x = (e.clientX - rect.left - pan.x) / zoom;
    let y = (e.clientY - rect.top - pan.y) / zoom;
    if (snapToGrid) {
      x = Math.round(x / 20) * 20;
      y = Math.round(y / 20) * 20;
    }
    return { x, y };
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      setIsPanning(true);
      setLastPan({ x: e.clientX, y: e.clientY });
      return;
    }
    const p = getCanvasPoint(e);

    if (tool === "edit" && selectedField) {
      // Check if clicked near a vertex
      const nearVertex = selectedField.points.findIndex(vp =>
        Math.sqrt((vp.x - p.x)**2 + (vp.y - p.y)**2) < 15
      );
      if (nearVertex >= 0) {
        // Start dragging vertex
        return;
      }
    }

    if (tool === "measure") {
      if (points.length >= 2) setPoints([p]);
      else setPoints([...points, p]);
      return;
    }

    if (tool === "polygon") {
      // Check if closing polygon
      if (points.length >= 3) {
        const first = points[0];
        if (Math.sqrt((first.x - p.x)**2 + (first.y - p.y)**2) < 15) {
          // Close polygon
          finishDrawing();
          return;
        }
      }
      setPoints([...points, p]);
      setIsDrawing(true);
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (isPanning) {
      const dx = e.clientX - lastPan.x;
      const dy = e.clientY - lastPan.y;
      setPan({ x: pan.x + dx, y: pan.y + dy });
      setLastPan({ x: e.clientX, y: e.clientY });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    if (tool === "rectangle" || tool === "circle") {
      setIsDrawing(false);
    }
  };

  const finishDrawing = () => {
    if (points.length < 3) return;
    // Calculate area using shoelace formula
    let area = 0;
    for (let i = 0; i < points.length; i++) {
      const j = (i + 1) % points.length;
      area += points[i].x * points[j].y;
      area -= points[j].x * points[i].y;
    }
    area = Math.abs(area) / 2 * 0.0001; // rough scale to hectares

    const newField: DrawnField = {
      id: Date.now(),
      name: fieldName || `حقل ${drawnFields.length + 1}`,
      points: [...points],
      area: Math.round(area * 100) / 100,
      crop: fieldCrop,
      color: "#367C2B",
    };
    setDrawnFields([...drawnFields, newField]);
    setPoints([]);
    setFieldName("");
    setSelectedField(newField);
  };

  const deleteField = (id: number) => {
    setDrawnFields(drawnFields.filter(f => f.id !== id));
    if (selectedField?.id === id) setSelectedField(null);
  };

  const undoLastPoint = () => {
    setPoints(points.slice(0, -1));
  };

  const clearPoints = () => {
    setPoints([]);
    setIsDrawing(false);
  };

  return (
    <div className="flex flex-col gap-3 h-full">
      {/* Toolbar */}
      <Card>
        <div className="p-2.5 flex gap-2 items-center flex-wrap">
          <div className="flex gap-1">
            {DRAW_TOOLS.map(t => {
              const isActive = tool === t.id;
              return (
                <button key={t.id} onClick={() => { setTool(t.id); setPoints([]); }}
                  title={t.desc}
                  className="px-2.5 py-1.5 rounded text-[10px] font-bold transition-all cursor-pointer border flex flex-col items-center gap-0.5"
                  style={{
                    background: isActive ? `${JD.green}15` : "transparent",
                    color: isActive ? JD.greenGlow : JD.textMuted,
                    borderColor: isActive ? `${JD.green}30` : "transparent",
                    minWidth: 56,
                  }}>
                  <span className="text-sm">{t.icon}</span>
                  <span>{t.label}</span>
                </button>
              );
            })}
          </div>
          <div className="w-px h-6 mx-1" style={{ background: JD.border }} />
          <div className="flex gap-2 items-center">
            <label className="flex items-center gap-1.5 text-[10px] cursor-pointer" style={{ color: JD.textMuted }}>
              <input type="checkbox" checked={showGrid} onChange={e => setShowGrid(e.target.checked)}
                className="w-3 h-3 rounded" />
              الشبكة
            </label>
            <label className="flex items-center gap-1.5 text-[10px] cursor-pointer" style={{ color: JD.textMuted }}>
              <input type="checkbox" checked={snapToGrid} onChange={e => setSnapToGrid(e.target.checked)}
                className="w-3 h-3 rounded" />
              التقاط
            </label>
          </div>
          <div className="mr-auto flex gap-2">
            <BtnGhost label="↺ تراجع" onClick={undoLastPoint} />
            <BtnGhost label="✕ مسح" onClick={clearPoints} />
            <BtnPrimary label="✓ إنهاء" onClick={finishDrawing} />
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_280px] gap-3 flex-1 min-h-0">
        {/* Canvas */}
        <div className="rounded-lg overflow-hidden relative" style={{ background: JD.surface, border: `1px solid ${JD.border}` }}>
          <canvas
            ref={canvasRef}
            width={800}
            height={500}
            className="w-full h-full cursor-crosshair"
            style={{ imageRendering: "auto" }}
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
          />

          {/* Zoom controls */}
          <div className="absolute right-3 bottom-3 flex flex-col gap-1">
            <button onClick={() => setZoom(Math.min(zoom + 0.2, 3))}
              className="w-8 h-8 rounded flex items-center justify-center text-sm font-bold cursor-pointer"
              style={{ background: "rgba(5,10,20,.9)", border: `1px solid ${JD.border}`, color: JD.text }}>+</button>
            <div className="text-center text-[9px] font-mono" style={{ color: JD.textMuted }}>{Math.round(zoom * 100)}%</div>
            <button onClick={() => setZoom(Math.max(zoom - 0.2, 0.5))}
              className="w-8 h-8 rounded flex items-center justify-center text-sm font-bold cursor-pointer"
              style={{ background: "rgba(5,10,20,.9)", border: `1px solid ${JD.border}`, color: JD.text }}>−</button>
          </div>

          {/* Info badge */}
          <div className="absolute top-3 left-3 rounded px-2.5 py-1.5 text-[9px]"
            style={{ background: "rgba(5,10,20,.85)", color: JD.textMuted }}>
            🛠 {DRAW_TOOLS.find(t => t.id === tool)?.label} · {points.length} نقطة · Alt+سحب للتحريك
          </div>

          {/* Coordinate readout */}
          <div className="absolute bottom-3 left-3 rounded px-2 py-1 text-[9px] font-mono"
            style={{ background: "rgba(5,10,20,.85)", color: JD.textMuted }}>
            Zoom: {zoom.toFixed(1)}x | Pan: {pan.x},{pan.y}
          </div>
        </div>

        {/* Side panel */}
        <div className="flex flex-col gap-3 overflow-y-auto" style={{ scrollbarWidth: "none" }}>
          {/* Field properties */}
          <Card>
            <SectionHeader title="خصائص الحقل" />
            <div className="p-3 space-y-2.5">
              <div>
                <label className="text-[9px] font-bold block mb-1" style={{ color: JD.textMuted }}>اسم الحقل</label>
                <input value={fieldName} onChange={e => setFieldName(e.target.value)}
                  placeholder="مثال: حقل الشمال الجديد"
                  className="w-full px-2.5 py-1.5 rounded text-[11px] border outline-none"
                  style={{ background: "#0a1520", color: JD.text, borderColor: JD.border }} />
              </div>
              <div>
                <label className="text-[9px] font-bold block mb-1" style={{ color: JD.textMuted }}>المحصول</label>
                <select value={fieldCrop} onChange={e => setFieldCrop(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded text-[11px] border outline-none cursor-pointer"
                  style={{ background: "#0a1520", color: JD.text, borderColor: JD.border }}>
                  <option>قمح</option><option>ذرة</option><option>بن</option><option>طماطم</option><option>أرز</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                  <div className="text-[9px]" style={{ color: JD.textMuted }}>النقاط</div>
                  <div className="text-sm font-black" style={{ color: JD.greenGlow }}>{points.length}</div>
                </div>
                <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                  <div className="text-[9px]" style={{ color: JD.textMuted }}>المساحة (تقديرية)</div>
                  <div className="text-sm font-black" style={{ color: JD.yellow }}>
                    {points.length >= 3 ? (Math.abs(points.reduce((a, p, i) => {
                      const j = (i + 1) % points.length;
                      return a + p.x * points[j].y - points[j].x * p.y;
                    }, 0)) / 2 * 0.0001).toFixed(2) : "0.00"} هـ
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Drawn fields list */}
          <Card>
            <SectionHeader title={`الحقول المرسومة (${drawnFields.length})`} />
            <div className="overflow-y-auto" style={{ maxHeight: 280, scrollbarWidth: "none" }}>
              {drawnFields.map(df => {
                const isSel = selectedField?.id === df.id;
                return (
                  <div key={df.id} onClick={() => setSelectedField(isSel ? null : df)}
                    className="px-3 py-2.5 cursor-pointer border-b transition-all"
                    style={{
                      borderColor: JD.border,
                      background: isSel ? "rgba(54,124,43,.06)" : "transparent",
                      borderRight: isSel ? `2px solid ${JD.greenGlow}` : "2px solid transparent",
                    }}>
                    <div className="flex justify-between items-center">
                      <span className="text-[10px] font-bold" style={{ color: isSel ? JD.text : JD.textSub }}>{df.name}</span>
                      <button onClick={(e) => { e.stopPropagation(); deleteField(df.id); }}
                        className="text-[9px] px-1.5 py-0.5 rounded cursor-pointer hover:bg-red-500/10"
                        style={{ color: JD.red }}>🗑</button>
                    </div>
                    <div className="text-[8px] mt-0.5" style={{ color: JD.textMuted }}>
                      {df.area} هـ · {df.crop} · {df.points.length} نقطة
                    </div>
                  </div>
                );
              })}
            </div>
          </Card>

          {/* Import/Export */}
          <Card className="p-3">
            <div className="text-[10px] font-bold mb-2" style={{ color: JD.text }}>استيراد / تصدير</div>
            <div className="flex gap-2 flex-wrap">
              <BtnGhost label="📁 KML" size="xs" />
              <BtnGhost label="📁 SHP" size="xs" />
              <BtnGhost label="📁 GeoJSON" size="xs" />
              <BtnGhost label="⬇ تصدير الكل" size="xs" />
            </div>
            <div className="mt-2 text-[8px] leading-relaxed" style={{ color: JD.textMuted }}>
              يدعم استيراد الحدود من John Deere Operations Center، Trimble، وQGIS.
            </div>
          </Card>

          {/* Tips */}
          <div className="rounded-lg p-3" style={{ background: "rgba(56,189,248,.05)", border: "1px solid rgba(56,189,248,.15)" }}>
            <div className="text-[10px] font-bold mb-1" style={{ color: JD.blue }}>💡 نصائح الرسم</div>
            <ul className="text-[9px] leading-relaxed space-y-1" style={{ color: JD.textMuted }}>
              <li>• انقر لإضافة نقطة، انقر على النقطة الأولى لإغلاق المضلع</li>
              <li>• Alt + سحب للتحريك في الخريطة</li>
              <li>• استخدم التقاط الشبكة لدقة أعلى</li>
              <li>• يمكن استيراد حدود CLU من الخرائط القمرية</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  NEW: FINANCE & INSURANCE
═══════════════════════════════════════════════════════════════ */
function FinanceScreen() {
  const [filter, setFilter] = useState("الكل");
  const filtered = filter === "الكل" ? FINANCE_DATA : FINANCE_DATA.filter(f => f.type === filter);

  const totalCoverage = FINANCE_DATA.filter(f => f.type === "تأمين" && f.status === "نشط").reduce((s, f) => s + f.coverage, 0);
  const totalLoans = FINANCE_DATA.filter(f => f.type === "قرض" || f.type === "تمويل").reduce((s, f) => s + f.amount, 0);
  const activeCount = FINANCE_DATA.filter(f => f.status === "نشط").length;

  return (
    <div className="flex flex-col gap-3">
      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        <KpiTile label="التغطية التأمينية" value={totalCoverage.toLocaleString()} unit="ريال" color={JD.greenGlow} icon="🛡" trend={8} />
        <KpiTile label="القروض المستحقة" value={totalLoans.toLocaleString()} unit="ريال" color={JD.orange} icon="💰" trend={-3} />
        <KpiTile label="عقود نشطة" value={activeCount} unit="عقد" color={JD.blue} icon="📋" trend={0} />
        <KpiTile label="أقساط شهرية" value="24,500" unit="ريال" color={JD.purple} icon="📅" trend={2} />
      </div>

      <Card>
        <div className="p-2.5 flex gap-2 items-center flex-wrap">
          <span className="text-sm font-bold" style={{ color: JD.text }}>التمويل والتأمين</span>
          <TabStrip options={["الكل", "تأمين", "قرض", "تمويل"]} active={filter} onChange={setFilter} />
          <div className="mr-auto"><BtnPrimary label="+ عقد جديد" /></div>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {filtered.map(item => {
          const isInsurance = item.type === "تأمين";
          const statusColor = item.status === "نشط" ? JD.greenGlow : JD.orange;
          return (
            <Card key={item.id} style={{ borderTop: `2px solid ${isInsurance ? JD.blue : JD.orange}` }}>
              <div className="p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <div className="text-sm font-bold" style={{ color: JD.text }}>{item.title}</div>
                    <div className="text-[9px] mt-0.5" style={{ color: JD.textMuted }}>{item.provider}</div>
                  </div>
                  <Pill label={item.status} color={statusColor} size="xs" />
                </div>

                <div className="grid grid-cols-2 gap-2 mb-3">
                  {isInsurance ? (
                    <>
                      <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                        <div className="text-sm font-black tabular-nums" style={{ color: JD.blue }}>{item.premium?.toLocaleString()}</div>
                        <div className="text-[8px]" style={{ color: JD.textMuted }}>القسط (ريال)</div>
                      </div>
                      <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                        <div className="text-sm font-black tabular-nums" style={{ color: JD.greenGlow }}>{item.coverage?.toLocaleString()}</div>
                        <div className="text-[8px]" style={{ color: JD.textMuted }}>التغطية (ريال)</div>
                      </div>
                    </>
                  ) : (
                    <>
                      <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                        <div className="text-sm font-black tabular-nums" style={{ color: JD.orange }}>{item.amount?.toLocaleString()}</div>
                        <div className="text-[8px]" style={{ color: JD.textMuted }}>المبلغ (ريال)</div>
                      </div>
                      <div className="rounded p-2 text-center" style={{ background: "#0a1520" }}>
                        <div className="text-sm font-black tabular-nums" style={{ color: JD.yellow }}>{item.rate}</div>
                        <div className="text-[8px]" style={{ color: JD.textMuted }}>الفائدة</div>
                      </div>
                    </>
                  )}
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-[9px]" style={{ color: JD.textMuted }}>الاستحقاق: {item.due}</span>
                  <div className="flex gap-1.5">
                    <BtnGhost label="📄 عقد" size="xs" />
                    <BtnGhost label="🔄 تجديد" size="xs" />
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Risk assessment */}
      <Card className="p-4">
        <div className="text-xs font-bold mb-3" style={{ color: JD.text }}>تقييم المخاطر — موسم 2026</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {[
            { risk: "جفاف", prob: 35, impact: "متوسط", color: JD.orange, mitigation: "ري بالتنقيط + تغطية تأمينية" },
            { risk: "آفات", prob: 22, impact: "منخفض", color: JD.greenGlow, mitigation: "رش وقائي + مراقبة IoT" },
            { risk: "فيضان", prob: 8, impact: "حرج", color: JD.red, mitigation: "تصريف مائي + تأمين محاصيل" },
          ].map(r => (
            <div key={r.risk} className="rounded-md p-3" style={{ background: "#0a1520", border: `1px solid ${JD.border}` }}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-[10px] font-bold" style={{ color: JD.text }}>{r.risk}</span>
                <Pill label={`${r.prob}%`} color={r.color} size="xs" />
              </div>
              <div className="text-[9px] mb-1" style={{ color: JD.textMuted }}>التأثير: <span style={{ color: r.color }}>{r.impact}</span></div>
              <div className="text-[8px] leading-relaxed" style={{ color: JD.textSub }}>🛡 {r.mitigation}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  NEW: CARBON CREDITS
═══════════════════════════════════════════════════════════════ */
function CarbonScreen() {
  const progress = (CARBON_DATA.totalSequestered / CARBON_DATA.target) * 100;
  const creditValue = CARBON_DATA.credits * CARBON_DATA.price;

  return (
    <div className="flex flex-col gap-3">
      {/* KPIs */}
      <div className="grid grid-cols-2 xl:grid-cols-4 gap-3">
        <KpiTile label="كربون مخزن" value={CARBON_DATA.totalSequestered} unit="طن" color={JD.greenGlow} icon="🌱" trend={12} />
        <KpiTile label="الهدف السنوي" value={CARBON_DATA.target} unit="طن" color={JD.cyan} icon="🎯" trend={0} />
        <KpiTile label="رصيد الاعتمادات" value={CARBON_DATA.credits} unit="credit" color={JD.yellow} icon="💎" trend={8} />
        <KpiTile label="القيمة السوقية" value={creditValue.toLocaleString()} unit="$" color={JD.blue} icon="💵" trend={15} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_300px] gap-3">
        {/* Progress & Chart */}
        <div className="flex flex-col gap-3">
          <Card className="p-4">
            <div className="flex justify-between items-start mb-3">
              <div>
                <div className="text-sm font-bold" style={{ color: JD.text }}>تقدم التخزين الكربوني</div>
                <div className="text-[9px] mt-0.5" style={{ color: JD.textMuted }}>الموسم 2026 · FAO Carbon Methodology</div>
              </div>
              <div className="text-left">
                <div className="text-2xl font-black tabular-nums leading-none" style={{ color: JD.greenGlow }}>{progress.toFixed(1)}%</div>
                <div className="text-[9px]" style={{ color: JD.textMuted }}>من الهدف</div>
              </div>
            </div>
            <div className="h-2.5 rounded-full overflow-hidden mb-3" style={{ background: "#0a1520" }}>
              <div className="h-full rounded-full transition-all duration-1000"
                style={{ width: `${progress}%`, background: `linear-gradient(90deg,${JD.green},${JD.greenGlow})` }} />
            </div>
            <div className="flex justify-between text-[9px]" style={{ color: JD.textMuted }}>
              <span>يناير</span><span>فبراير</span><span>مارس</span><span>أبريل</span><span>مايو ←</span><span>الهدف</span>
            </div>
          </Card>

          <Card className="p-4">
            <div className="text-xs font-bold mb-3" style={{ color: JD.text }}>المخزن مقابل الانبعاثات — شهرياً</div>
            <MultiLine series={[
              { label: "مخزن", data: CARBON_DATA.history.map(h => h.sequestered), color: JD.greenGlow },
              { label: "انبعاث", data: CARBON_DATA.history.map(h => h.emitted), color: JD.red },
            ]} h={140} />
            <div className="flex justify-between text-[8px] mt-1.5 px-1" style={{ color: JD.textMuted }}>
              {CARBON_DATA.history.map(h => <span key={h.month}>{h.month}</span>)}
            </div>
          </Card>
        </div>

        {/* Practices & Market */}
        <div className="flex flex-col gap-3">
          <Card>
            <SectionHeader title="الممارسات المناخية" />
            <div className="p-3 space-y-2">
              {CARBON_DATA.practices.map((p, i) => (
                <div key={p.name} className="flex items-center gap-2.5 p-2 rounded" style={{ background: "#0a1520" }}>
                  <div className="w-8 h-8 rounded flex items-center justify-center text-[10px] font-black flex-shrink-0"
                    style={{ background: `${JD.greenGlow}15`, color: JD.greenGlow }}>
                    {i + 1}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-[10px] font-bold" style={{ color: JD.text }}>{p.name}</div>
                    <div className="text-[9px]" style={{ color: JD.textMuted }}>تأثير: {p.impact} طن CO₂e</div>
                  </div>
                  <Pill label={p.status} color={p.status === "مطبق" ? JD.greenGlow : JD.orange} size="xs" />
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-4">
            <div className="text-xs font-bold mb-3" style={{ color: JD.text }}>سوق الاعتمادات الكربونية</div>
            <div className="space-y-2">
              {[
                { market: "Verra VCS", price: 45, vol: "12.5K", trend: "↑ 3%" },
                { market: "Gold Standard", price: 52, vol: "8.2K", trend: "↑ 5%" },
                { market: "Climate Action Reserve", price: 38, vol: "5.1K", trend: "↓ 1%" },
              ].map(m => (
                <div key={m.market} className="flex justify-between items-center py-2" style={{ borderBottom: `1px solid ${JD.border}` }}>
                  <div>
                    <div className="text-[10px] font-bold" style={{ color: JD.text }}>{m.market}</div>
                    <div className="text-[8px]" style={{ color: JD.textMuted }}>حجم: {m.vol}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-black" style={{ color: JD.yellow }}>${m.price}</div>
                    <div className="text-[8px]" style={{ color: m.trend.includes("↑") ? JD.greenGlow : JD.red }}>{m.trend}</div>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <div className="rounded-lg p-3" style={{ background: "rgba(16,185,129,.05)", border: "1px solid rgba(16,185,129,.15)" }}>
            <div className="text-[10px] font-bold mb-1" style={{ color: JD.greenGlow }}>✓ متوافق مع</div>
            <div className="flex flex-wrap gap-1.5">
              {["Verra VCS", "Gold Standard", "CDM", "ISO 14064"].map(std => (
                <Pill key={std} label={std} size="xs" />
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


/* ═══════════════════════════════════════════════════════════════
  MAIN APP
═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════
  MAIN APP
═══════════════════════════════════════════════════════════════ */
export default function App() {
  const [screen, setScreen] = useState<ScreenId>("dash");
  const [collapsed, setCollapsed] = useState(false);
  const field = FIELDS[0];
  const alertCount = FIELDS.filter(f => f.st !== "g").length;
  const activeLabel = SCREENS.find(s => s.id === screen)?.label || "";

  const renderScreen = () => {
    switch (screen) {
      case "dash": return <Dashboard fields={FIELDS} go={setScreen} />;
      case "map": return <MapScreen field={field} fields={FIELDS} />;
      case "idx": return <IndicesPanel />;
      case "ts": return <TimeSeries field={field} />;
      case "rep": return <Reports field={field} />;
      case "wx": return <Weather />;
      case "scout": return <ScoutingScreen fields={FIELDS} />;
      case "ai": return <AIChat />;
      case "sensor": return <Sensors />;
      case "tasks": return <TasksScreen />;
      case "team": return <TeamScreen />;
      case "vra": return <VRAScreen />;
      case "trace": return <TraceScreen />;
      case "machines": return <MachinesScreen />;
      case "draw": return <DrawingToolsScreen fields={FIELDS} />;
      case "finance": return <FinanceScreen />;
      case "carbon": return <CarbonScreen />;
      default: return <Dashboard fields={FIELDS} go={setScreen} />;
    }
  };

  return (
    <div className="h-screen w-screen flex overflow-hidden" style={{ background: JD.bg, direction: "rtl" }}>
      <style>{`
        @keyframes bounce { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }
        ::-webkit-scrollbar{width:4px;height:4px}
        ::-webkit-scrollbar-track{background:transparent}
        ::-webkit-scrollbar-thumb{background:#1a2840;border-radius:2px}
        ::-webkit-scrollbar-thumb:hover{background:#243650}
        * { box-sizing: border-box; }
      `}</style>

      <Sidebar active={screen} go={setScreen} collapsed={collapsed} setCollapsed={setCollapsed} />

      <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <TopBar label={activeLabel} alertCount={alertCount} />
        <div className="flex-1 overflow-y-auto p-4">
          {renderScreen()}
          <div className="h-6" />
        </div>
      </main>
    </div>
  );
}
