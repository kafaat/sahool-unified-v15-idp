import { useState, useRef, useEffect } from "react";

/* ═══════════════════════════════════════════════════════════════
  DATA
═══════════════════════════════════════════════════════════════ */
const FIELDS = [
  {id:1,n:"حقل الشمال",    crop:"قمح",   area:"2.4", ndvi:.78, ec:1.1, moist:52, elev:820, st:"g", dir:[], lat:24.5, lng:46.7},
  {id:2,n:"الوادي الأوسط", crop:"ذرة",   area:"1.8", ndvi:.61, ec:1.8, moist:38, elev:760, st:"a", dir:["NW","SW"], lat:24.48, lng:46.72},
  {id:3,n:"المدرج الجنوبي",crop:"بن",    area:"3.1", ndvi:.85, ec:.9,  moist:68, elev:1180,st:"g", dir:[], lat:24.45, lng:46.68},
  {id:4,n:"حوض الغرب",     crop:"طماطم", area:"0.9", ndvi:.44, ec:2.4, moist:28, elev:690, st:"r", dir:["W","SW"], lat:24.52, lng:46.65},
  {id:5,n:"المزرعة الشرقية",crop:"أرز",  area:"4.2", ndvi:.72, ec:1.3, moist:55, elev:840, st:"g", dir:["E"], lat:24.55, lng:46.78},
];

const ALL_INDICES = [
  {id:"hybrid",  lab:"Hybrid",  cat:"أساسي",       c:"#10B981", desc:"يجمع NDVI+NDWI في صورة واحدة"},
  {id:"ndvi",    lab:"NDVI",    cat:"صحة مبكرة",   c:"#22C55E", desc:"الصحة الخضرية العامة"},
  {id:"evi",     lab:"EVI",     cat:"صحة مبكرة",   c:"#4ADE80", desc:"تصحيح جوي وتربة"},
  {id:"savi",    lab:"SAVI",    cat:"صحة مبكرة",   c:"#86EFAC", desc:"تصحيح تأثير التربة"},
  {id:"ndre",    lab:"NDRE",    cat:"صحة متأخرة",  c:"#A3E635", desc:"للكثافة العالية"},
  {id:"ndwi",    lab:"NDWI",    cat:"ري",           c:"#38BDF8", desc:"نقص الماء في الأوراق"},
  {id:"et",      lab:"ET",      cat:"ري",           c:"#7DD3FC", desc:"التبخر النتحي"},
  {id:"ndmi",    lab:"NDMI",    cat:"ري",           c:"#BAE6FD", desc:"رطوبة التربة"},
  {id:"soc",     lab:"SOC",     cat:"تربة",         c:"#D97706", desc:"الكربون العضوي"},
  {id:"erosion", lab:"Erosion", cat:"تربة",         c:"#EF4444", desc:"تآكل التربة"},
  {id:"dem",     lab:"DEM",     cat:"تضاريس",       c:"#8B5CF6", desc:"نموذج الارتفاع الرقمي"},
  {id:"rvi",     lab:"RVI",     cat:"SAR رادار",    c:"#F59E0B", desc:"صحة المحصول بالرادار"},
  {id:"rsm",     lab:"RSM",     cat:"SAR رادار",    c:"#FCD34D", desc:"رطوبة التربة بالرادار"},
  {id:"tci",     lab:"TCI",     cat:"صورة",         c:"#0EA5E9", desc:"صورة قمرية طبيعية"},
  {id:"etci",    lab:"ETCI",    cat:"صورة",         c:"#38BDF8", desc:"صورة محسّنة"},
  {id:"cb",      lab:"CB",      cat:"وصول",         c:"#94A3B8", desc:"نمط لعمى الألوان"},
];

const JD = {
  green: "#367C2B", greenDark: "#1e5218", greenLight: "#3f9e30", greenGlow: "#4caf50",
  yellow: "#FFDE00", yellowDark: "#e6c800",
  bg: "#090e18", panel: "#0d1520", surface: "#111a27", surfaceHigh: "#152030", surfaceHover: "#192638",
  border: "#1a2840", borderLight: "#243650",
  text: "#e2edf8", textSub: "#8baec9", textMuted: "#3d5a78",
  red: "#ef4444", orange: "#f59e0b", blue: "#38bdf8", purple: "#8b5cf6", cyan: "#22d3ee",
};

const stc = (s:string) => s==="g"?JD.greenGlow:s==="a"?JD.orange:JD.red;
const ndviColor = (v:number) => v<.1?"#8B0000":v<.2?"#CC3300":v<.3?"#FF6600":v<.37?"#FFC107":v<.45?"#CDDC39":v<.55?"#66BB6A":"#2E7D32";

/* ═══════════════════════════════════════════════════════════════
  ATOMS
═══════════════════════════════════════════════════════════════ */
function Pill({label,color,bg,size="sm"}:{label:string;color?:string;bg?:string;size?:"xs"|"sm"}) {
  const col = color || JD.greenGlow;
  const sz = size==="xs" ? "px-1.5 py-px text-[9px]" : "px-2 py-0.5 text-[10px]";
  return (
    <span className={`inline-flex items-center rounded-sm font-bold whitespace-nowrap border ${sz}`}
      style={{background:bg||`${col}15`,color:col,borderColor:`${col}35`}}>{label}</span>
  );
}

function BtnPrimary({label,onClick,icon}:{label:string;onClick?:()=>void;icon?:string}) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-bold transition-all hover:brightness-110 active:scale-95 cursor-pointer"
      style={{background:`linear-gradient(135deg,${JD.green},${JD.greenDark})`,color:"#fff",boxShadow:`0 1px 8px ${JD.green}30`}}>
      {icon && <span>{icon}</span>}{label}
    </button>
  );
}

function BtnGhost({label,onClick,icon}:{label:string;onClick?:()=>void;icon?:string}) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded text-[11px] font-bold transition-all hover:bg-white/5 active:scale-95 cursor-pointer border"
      style={{color:JD.textSub,borderColor:JD.border}}>
      {icon && <span>{icon}</span>}{label}
    </button>
  );
}

function Card({children,className="",style,onClick}:{children:React.ReactNode;className?:string;style?:React.CSSProperties;onClick?:()=>void}) {
  return (
    <div onClick={onClick}
      className={`rounded-lg overflow-hidden ${className} ${onClick?"cursor-pointer hover:border-opacity-60 transition-colors":""}`}
      style={{background:JD.surface,border:`1px solid ${JD.border}`,...style}}>{children}</div>
  );
}

/* ═══════════════════════════════════════════════════════════════
  NDVI OVERLAY GRADIENT — generates color overlay for fields
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

export default function MapScreen() {
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
