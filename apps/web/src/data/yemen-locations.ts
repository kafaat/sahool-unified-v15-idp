/**
 * Yemen administrative divisions — Governorates & Districts
 * Coordinates: WGS84 [lat, lng] — Leaflet-compatible
 * Sources: OCHA Yemen (HDX), Wikipedia, GeoNames
 */

export interface YemenDistrict {
  nameAr: string;
  nameEn: string;
  center: [number, number]; // [lat, lng]
}

export interface YemenGovernorate {
  nameAr: string;
  nameEn: string;
  center: [number, number];
  districts: YemenDistrict[];
}

export const YEMEN_GOVERNORATES: YemenGovernorate[] = [
  // ─── 1. أمانة العاصمة ───────────────────────────────────────────────────────
  {
    nameAr: 'أمانة العاصمة',
    nameEn: 'Amanat Al Asimah',
    center: [15.3547, 44.2067],
    districts: [
      { nameAr: 'آزال',       nameEn: 'Azal',           center: [15.382, 44.194] },
      { nameAr: 'معين',       nameEn: "Ma'ain",          center: [15.340, 44.163] },
      { nameAr: 'التحرير',   nameEn: 'At Tahrir',       center: [15.360, 44.200] },
      { nameAr: 'السبعين',   nameEn: 'As Sabain',       center: [15.352, 44.213] },
      { nameAr: 'شعوب',      nameEn: "Shu'ub",          center: [15.374, 44.182] },
      { nameAr: 'الثورة',    nameEn: 'Ath Thawrah',     center: [15.363, 44.230] },
      { nameAr: 'بني الحارث',nameEn: 'Bani Al Harith',  center: [15.430, 44.147] },
      { nameAr: 'همدان',     nameEn: 'Hamdan',           center: [15.310, 44.127] },
    ],
  },

  // ─── 2. صنعاء ────────────────────────────────────────────────────────────────
  {
    nameAr: 'صنعاء',
    nameEn: "Sana'a",
    center: [15.350, 44.200],
    districts: [
      { nameAr: 'أرحب',                  nameEn: 'Arhab',                   center: [15.533, 44.383] },
      { nameAr: 'بني حشيش',             nameEn: 'Bani Hashish',            center: [15.400, 44.550] },
      { nameAr: 'بني مطر',              nameEn: 'Bani Matar',              center: [15.200, 43.933] },
      { nameAr: 'بئر العبد',            nameEn: 'Bir Al Abd',              center: [15.150, 44.117] },
      { nameAr: 'ذهبان',                nameEn: 'Dhahban',                 center: [15.483, 43.883] },
      { nameAr: 'همدان',                nameEn: 'Hamdan',                  center: [15.250, 44.083] },
      { nameAr: 'حزيز',                 nameEn: 'Haziz',                   center: [15.267, 44.233] },
      { nameAr: 'الحيمة الداخلية',      nameEn: 'Al Haymah Ad Dakhiliyah', center: [15.017, 44.050] },
      { nameAr: 'الحيمة الخارجية',      nameEn: 'Al Haymah Al Kharijiyah', center: [14.850, 43.817] },
      { nameAr: 'خولان',                nameEn: 'Khawlan',                 center: [15.483, 44.567] },
      { nameAr: 'مناخة',                nameEn: 'Manakhah',                center: [15.083, 43.733] },
      { nameAr: 'نهم',                  nameEn: 'Nihm',                    center: [15.517, 44.783] },
      { nameAr: 'الروضة',               nameEn: 'Al Rawdah',               center: [15.480, 44.280] },
      { nameAr: 'صنهان',                nameEn: 'Sanhan',                  center: [15.183, 44.267] },
      { nameAr: 'بلاد الروس',           nameEn: 'Bilad Ar Rus',            center: [15.383, 43.850] },
      { nameAr: 'ريدة وقفر',            nameEn: 'Rida wa Qufar',           center: [15.617, 43.967] },
    ],
  },

  // ─── 3. عدن ──────────────────────────────────────────────────────────────────
  {
    nameAr: 'عدن',
    nameEn: 'Aden',
    center: [12.783, 45.033],
    districts: [
      { nameAr: 'التواهي',      nameEn: 'At Tawahi',       center: [12.753, 44.943] },
      { nameAr: 'المعلا',       nameEn: "Al Mu'alla",      center: [12.767, 45.000] },
      { nameAr: 'الكريتر',     nameEn: 'Al Crater',       center: [12.780, 45.020] },
      { nameAr: 'الشيخ عثمان', nameEn: 'Ash Sheikh Uthman',center: [12.867, 45.017] },
      { nameAr: 'خور مكسر',    nameEn: 'Khur Maksar',     center: [12.793, 45.050] },
      { nameAr: 'البريقة',      nameEn: 'Al Buraiqa',      center: [12.803, 44.967] },
      { nameAr: 'المنصورة',     nameEn: 'Al Mansura',      center: [12.817, 45.033] },
      { nameAr: 'دار سعد',      nameEn: 'Dar Saad',        center: [12.900, 45.083] },
    ],
  },

  // ─── 4. تعز ──────────────────────────────────────────────────────────────────
  {
    nameAr: 'تعز',
    nameEn: 'Taiz',
    center: [13.567, 44.017],
    districts: [
      { nameAr: 'القاهرة',      nameEn: 'Al Qahirah',        center: [13.577, 44.022] },
      { nameAr: 'المظفر',       nameEn: 'Al Mudhaffar',      center: [13.580, 44.030] },
      { nameAr: 'الأشرفية',     nameEn: 'Al Ashrafiyah',     center: [13.570, 44.018] },
      { nameAr: 'صبر الموادم',  nameEn: 'Sabir Al Mawadim',  center: [13.483, 44.133] },
      { nameAr: 'المواهب',      nameEn: 'Al Mawahib',        center: [13.667, 44.000] },
      { nameAr: 'المعافر',      nameEn: "Al Ma'afer",        center: [13.483, 44.000] },
      { nameAr: 'الحوبان',      nameEn: 'Al Hawban',         center: [13.633, 44.083] },
      { nameAr: 'شرعب السلام',  nameEn: "Sha'ub As Salam",   center: [13.333, 43.817] },
      { nameAr: 'شرعب الرونة',  nameEn: "Sha'ub Ar Rawnah",  center: [13.400, 43.900] },
      { nameAr: 'مقبنة',        nameEn: 'Maqbanah',          center: [13.567, 43.633] },
      { nameAr: 'الوازعية',     nameEn: 'Al Wazi\'yah',      center: [13.633, 43.733] },
      { nameAr: 'المخا',        nameEn: 'Al Mokha',          center: [13.317, 43.250] },
      { nameAr: 'حيفان',        nameEn: 'Hayfan',            center: [13.650, 44.283] },
      { nameAr: 'المسراخ',      nameEn: 'Al Misrakh',        center: [13.367, 43.633] },
      { nameAr: 'ذي السفال',    nameEn: 'Dhi As Sufal',      center: [13.683, 44.133] },
      { nameAr: 'صالة',         nameEn: 'Salah',             center: [13.233, 43.583] },
      { nameAr: 'ماوية',        nameEn: 'Mawiyah',           center: [13.533, 44.400] },
      { nameAr: 'الربوعة',      nameEn: 'Ar Rubou\'ah',      center: [13.700, 43.817] },
      { nameAr: 'التعزية',      nameEn: 'At Ta\'iziyah',     center: [13.500, 43.900] },
      { nameAr: 'قحزة',         nameEn: 'Qahzah',            center: [13.417, 44.250] },
      { nameAr: 'الشمايتين',    nameEn: 'Ash Shamayatayn',   center: [13.217, 43.817] },
      { nameAr: 'جبل حبشي',     nameEn: 'Jabal Habashi',     center: [13.467, 44.033] },
      { nameAr: 'مضيبي',        nameEn: 'Mudaybi',           center: [13.350, 44.050] },
    ],
  },

  // ─── 5. الحديدة ──────────────────────────────────────────────────────────────
  {
    nameAr: 'الحديدة',
    nameEn: 'Al Hudaydah',
    center: [14.800, 42.950],
    districts: [
      { nameAr: 'الحديدة',      nameEn: 'Al Hudaydah',     center: [14.797, 42.954] },
      { nameAr: 'زبيد',         nameEn: 'Zabid',           center: [14.200, 43.317] },
      { nameAr: 'بيت الفقيه',   nameEn: 'Bayt Al Faqih',  center: [14.517, 43.317] },
      { nameAr: 'الدريهمي',     nameEn: 'Ad Durayhimi',    center: [14.683, 42.967] },
      { nameAr: 'الخوخة',       nameEn: 'Al Khawkhah',    center: [13.967, 43.233] },
      { nameAr: 'المراوعة',     nameEn: "Al Marawi'ah",    center: [14.883, 43.067] },
      { nameAr: 'باجل',         nameEn: 'Bajil',           center: [15.067, 43.300] },
      { nameAr: 'التحيتا',      nameEn: 'At Tuhayta',     center: [14.350, 43.100] },
      { nameAr: 'حيس',          nameEn: 'Hays',            center: [13.950, 43.383] },
      { nameAr: 'اللحية',       nameEn: 'Al Luhayyah',    center: [15.700, 42.683] },
      { nameAr: 'الصليف',       nameEn: 'As Salif',        center: [15.317, 42.683] },
      { nameAr: 'عبس',          nameEn: 'Abs',             center: [15.833, 43.417] },
      { nameAr: 'حيران',        nameEn: 'Hayran',          center: [16.000, 43.300] },
      { nameAr: 'الزهرة',       nameEn: 'Az Zuhrah',       center: [15.200, 43.333] },
      { nameAr: 'الجراحي',      nameEn: 'Al Jarahi',       center: [14.317, 43.250] },
      { nameAr: 'المنيرة',      nameEn: 'Al Munirah',      center: [14.733, 43.067] },
      { nameAr: 'المنصورية',    nameEn: 'Al Mansuriyah',   center: [14.833, 43.183] },
      { nameAr: 'الصخرة',       nameEn: 'As Sukhnah',      center: [14.550, 43.050] },
      { nameAr: 'كمران',        nameEn: 'Kamaran',         center: [15.350, 42.600] },
      { nameAr: 'القنواص',      nameEn: 'Al Qanawis',     center: [15.567, 43.150] },
      { nameAr: 'ميدي',         nameEn: 'Midi',            center: [16.317, 43.100] },
      { nameAr: 'حيس',          nameEn: 'Hays',            center: [13.950, 43.383] },
      { nameAr: 'الفازة',       nameEn: 'Al Fazah',        center: [14.900, 42.950] },
      { nameAr: 'المنصورية',    nameEn: 'Al Mansuriyah',   center: [14.833, 43.183] },
      { nameAr: 'قحلة',         nameEn: 'Qahlah',          center: [16.067, 43.450] },
      { nameAr: 'الحشا',        nameEn: 'Al Hisha',        center: [14.133, 43.283] },
      { nameAr: 'وادي العمارد', nameEn: 'Wadi Al Amarid',  center: [15.167, 42.933] },
    ],
  },

  // ─── 6. إب ───────────────────────────────────────────────────────────────────
  {
    nameAr: 'إب',
    nameEn: 'Ibb',
    center: [13.983, 44.183],
    districts: [
      { nameAr: 'إب',           nameEn: 'Ibb',              center: [13.976, 44.183] },
      { nameAr: 'الضبعة',       nameEn: "Ad Dab'ah",        center: [13.817, 44.117] },
      { nameAr: 'السبرة',       nameEn: 'As Sabrah',        center: [13.833, 44.283] },
      { nameAr: 'جبلة',         nameEn: 'Jubalah',          center: [13.833, 44.100] },
      { nameAr: 'يريم',         nameEn: 'Yarim',            center: [14.300, 44.383] },
      { nameAr: 'العدين',       nameEn: 'Al Adan',          center: [13.750, 43.867] },
      { nameAr: 'الحدأ',        nameEn: 'Al Hada',          center: [14.083, 43.800] },
      { nameAr: 'مفتاح',        nameEn: 'Miftah',           center: [13.967, 44.233] },
      { nameAr: 'حبيش',         nameEn: 'Hubaish',          center: [13.700, 44.133] },
      { nameAr: 'المخادر',      nameEn: 'Al Makhader',      center: [14.117, 44.483] },
      { nameAr: 'قعطبة',        nameEn: "Qa'atabah",        center: [13.533, 44.383] },
      { nameAr: 'ذو السفال',    nameEn: 'Dhu As Sufal',     center: [13.767, 44.250] },
      { nameAr: 'السياني',      nameEn: 'As Siyani',        center: [14.017, 44.317] },
      { nameAr: 'وصاب العالي',  nameEn: 'Wusab Al Ali',     center: [14.133, 44.033] },
      { nameAr: 'وصاب السافل',  nameEn: 'Wusab As Safil',   center: [14.050, 44.133] },
      { nameAr: 'الشعر',        nameEn: 'Ash Sha\'r',       center: [14.117, 44.267] },
      { nameAr: 'بعدان',        nameEn: "Ba'dan",           center: [13.767, 44.017] },
      { nameAr: 'النادرة',      nameEn: 'An Nadirah',       center: [13.933, 44.417] },
      { nameAr: 'الحجرية',      nameEn: 'Al Hujariyah',     center: [13.680, 44.200] },
      { nameAr: 'فرع المخادر',  nameEn: "Far' Al Makhader", center: [14.200, 44.550] },
    ],
  },

  // ─── 7. ذمار ─────────────────────────────────────────────────────────────────
  {
    nameAr: 'ذمار',
    nameEn: 'Dhamar',
    center: [14.550, 44.400],
    districts: [
      { nameAr: 'ذمار',          nameEn: 'Dhamar',          center: [14.542, 44.404] },
      { nameAr: 'عنس',           nameEn: 'Ans',             center: [14.783, 44.450] },
      { nameAr: 'مغرب عنس',      nameEn: 'Maghrab Ans',     center: [14.867, 44.367] },
      { nameAr: 'حياة',          nameEn: 'Hayat',           center: [14.450, 44.600] },
      { nameAr: 'دوران أنس',     nameEn: 'Dawran Ans',      center: [14.617, 44.500] },
      { nameAr: 'الحداء',        nameEn: "Al Hada'",        center: [14.317, 44.250] },
      { nameAr: 'الحدة',         nameEn: 'Al Haddah',       center: [14.683, 44.583] },
      { nameAr: 'جهران',         nameEn: 'Jahran',          center: [14.900, 44.133] },
      { nameAr: 'عتمة',          nameEn: 'Utmah',           center: [14.250, 44.083] },
      { nameAr: 'إدفعان',        nameEn: 'Idfah',           center: [14.400, 44.317] },
      { nameAr: 'ميفعة أنس',     nameEn: "Mifa'at Ans",     center: [14.633, 44.467] },
      { nameAr: 'وصاب العالي',   nameEn: 'Wusab Al Ali',    center: [14.100, 43.967] },
    ],
  },

  // ─── 8. البيضاء ──────────────────────────────────────────────────────────────
  {
    nameAr: 'البيضاء',
    nameEn: 'Al Bayda',
    center: [13.983, 45.567],
    districts: [
      { nameAr: 'البيضاء',       nameEn: 'Al Bayda',        center: [13.984, 45.573] },
      { nameAr: 'ذي ناعم',       nameEn: "Dhi Na'im",       center: [13.867, 45.367] },
      { nameAr: 'ناطع',          nameEn: "Nati'",           center: [13.850, 45.767] },
      { nameAr: 'الزاهر',        nameEn: 'Az Zahir',        center: [14.233, 45.267] },
      { nameAr: 'مسوبة',         nameEn: 'Maswabah',        center: [14.200, 46.050] },
      { nameAr: 'رداع',          nameEn: "Rada'",           center: [14.433, 44.833] },
      { nameAr: 'الصومعة',       nameEn: "As Sawma'ah",     center: [14.100, 44.717] },
      { nameAr: 'العرش',         nameEn: 'Al Arsh',         center: [13.867, 45.550] },
      { nameAr: 'القريشية',      nameEn: 'Al Qurayshiyah',  center: [13.550, 45.483] },
      { nameAr: 'ولد ربيع',      nameEn: "Wulad Rabi'",     center: [14.067, 45.317] },
      { nameAr: 'السوادية',      nameEn: 'As Suwaydiyah',   center: [14.483, 45.367] },
      { nameAr: 'الملاجم',       nameEn: 'Al Malajim',      center: [14.133, 45.083] },
    ],
  },

  // ─── 9. أبين ─────────────────────────────────────────────────────────────────
  {
    nameAr: 'أبين',
    nameEn: 'Abyan',
    center: [13.117, 45.367],
    districts: [
      { nameAr: 'زنجبار',  nameEn: 'Zinjibar', center: [13.124, 45.379] },
      { nameAr: 'جعار',    nameEn: "Ja'ar",    center: [13.217, 45.300] },
      { nameAr: 'شقرة',    nameEn: 'Shuqrah',  center: [13.350, 45.700] },
      { nameAr: 'مودية',   nameEn: 'Mudiyah',  center: [13.200, 46.150] },
      { nameAr: 'رصد',     nameEn: 'Rasad',    center: [13.350, 45.583] },
      { nameAr: 'لودر',    nameEn: 'Lawdar',   center: [13.700, 45.700] },
      { nameAr: 'خنفر',    nameEn: 'Khanfar',  center: [13.300, 45.083] },
      { nameAr: 'أحور',    nameEn: 'Ahwar',    center: [13.533, 46.683] },
      { nameAr: 'مصعبة',   nameEn: "Mus'abah", center: [12.950, 45.067] },
      { nameAr: 'سرار',    nameEn: 'Sirar',    center: [13.117, 45.600] },
      { nameAr: 'وضيعة',   nameEn: "Wadi'ah",  center: [13.067, 45.350] },
    ],
  },

  // ─── 10. شبوة ────────────────────────────────────────────────────────────────
  {
    nameAr: 'شبوة',
    nameEn: 'Shabwah',
    center: [14.533, 46.833],
    districts: [
      { nameAr: 'عتق',            nameEn: 'Ataq',            center: [14.547, 46.831] },
      { nameAr: 'عسيلان',         nameEn: 'Usaylan',         center: [14.967, 46.200] },
      { nameAr: 'بيحان',          nameEn: 'Bayhan',          center: [15.067, 45.733] },
      { nameAr: 'حريب',           nameEn: 'Harib',           center: [15.433, 45.483] },
      { nameAr: 'رضوم',           nameEn: 'Radum',           center: [14.317, 47.733] },
      { nameAr: 'نصاب',           nameEn: 'Nisab',           center: [14.517, 46.017] },
      { nameAr: 'ساه',            nameEn: 'Sah',             center: [14.133, 46.933] },
      { nameAr: 'عين',            nameEn: 'Ain',             center: [16.067, 47.933] },
      { nameAr: 'مرخة العليا',    nameEn: 'Markha Al Ulya',  center: [14.567, 47.100] },
      { nameAr: 'مرخة السفلى',    nameEn: 'Markha As Sufla', center: [14.233, 46.967] },
      { nameAr: 'جردان',          nameEn: 'Jardan',          center: [14.717, 47.617] },
      { nameAr: 'الطلح',          nameEn: 'At Talah',        center: [15.267, 46.383] },
      { nameAr: 'الروضة',         nameEn: 'Ar Rawdah',       center: [14.167, 46.683] },
      { nameAr: 'حريب القراء',    nameEn: 'Harib Al Qaramis',center: [15.333, 45.383] },
    ],
  },

  // ─── 11. حضرموت ──────────────────────────────────────────────────────────────
  {
    nameAr: 'حضرموت',
    nameEn: 'Hadramaut',
    center: [15.533, 48.133],
    districts: [
      { nameAr: 'المكلا',         nameEn: 'Al Mukalla',      center: [14.532, 49.128] },
      { nameAr: 'سيئون',          nameEn: "Say'un",          center: [15.942, 48.788] },
      { nameAr: 'شبام',           nameEn: 'Shibam',          center: [15.928, 48.627] },
      { nameAr: 'تريم',           nameEn: 'Tarim',           center: [16.050, 49.000] },
      { nameAr: 'الشحر',          nameEn: 'Ash Shihr',       center: [14.750, 49.600] },
      { nameAr: 'سيحوت',          nameEn: 'Sayhut',          center: [15.217, 51.267] },
      { nameAr: 'حجر',            nameEn: 'Hajar',           center: [14.933, 48.783] },
      { nameAr: 'الديس الشرقي',   nameEn: 'Ad Dis Ash Sharqi',center: [14.283, 50.483] },
      { nameAr: 'دوعن',           nameEn: "Daw'an",          center: [15.867, 48.667] },
      { nameAr: 'عمد',            nameEn: 'Umad',            center: [16.000, 48.833] },
      { nameAr: 'القطن',          nameEn: 'Al Qatn',         center: [15.817, 48.683] },
      { nameAr: 'رخية',           nameEn: 'Rukhiyah',        center: [16.067, 49.367] },
      { nameAr: 'يبعث',           nameEn: "Yab'uth",         center: [15.783, 48.117] },
      { nameAr: 'المسيلة',        nameEn: 'Al Masilah',      center: [16.133, 49.083] },
      { nameAr: 'الأحمر',         nameEn: 'Al Ahmar',        center: [15.467, 50.117] },
      { nameAr: 'الريدة وقصي',    nameEn: 'Ar Riydah wa Qusay', center: [16.000, 49.333] },
      { nameAr: 'غيل باوزير',     nameEn: 'Ghail Bawazir',   center: [15.467, 49.900] },
      { nameAr: 'غيل بن يمين',    nameEn: 'Ghail Bin Yamin', center: [15.833, 49.567] },
      { nameAr: 'البروم ودوعن',   nameEn: 'Al Burum wa Daw\'an', center: [15.650, 48.500] },
      { nameAr: 'بور',            nameEn: 'Bur',             center: [14.550, 50.383] },
      { nameAr: 'قصيعر',          nameEn: 'Qusayir',         center: [15.683, 50.783] },
      { nameAr: 'خلف',            nameEn: 'Khalaf',          center: [17.433, 49.833] },
      { nameAr: 'الضليعة',        nameEn: "Ad Dali'ah",      center: [14.833, 49.200] },
      { nameAr: 'المكلا المدينة', nameEn: 'Al Mukalla City', center: [14.543, 49.124] },
      { nameAr: 'وادي العين',     nameEn: 'Wadi Al Ain',     center: [15.117, 48.583] },
      { nameAr: 'حضرموت الوادي',  nameEn: 'Hadramaut Wadi',  center: [15.517, 48.417] },
      { nameAr: 'وادي المسيلة',   nameEn: 'Wadi Al Masilah', center: [16.050, 49.250] },
    ],
  },

  // ─── 12. المهرة ──────────────────────────────────────────────────────────────
  {
    nameAr: 'المهرة',
    nameEn: 'Al Mahrah',
    center: [16.200, 52.167],
    districts: [
      { nameAr: 'الغيضة',         nameEn: 'Al Ghaydah',      center: [16.202, 52.177] },
      { nameAr: 'حوف',            nameEn: 'Hawf',            center: [16.850, 52.533] },
      { nameAr: 'مناعة',          nameEn: "Mana'ah",         center: [16.467, 52.833] },
      { nameAr: 'رأس العارة',     nameEn: "Ras Al Ara",      center: [16.300, 52.333] },
      { nameAr: 'شحن',            nameEn: 'Shahn',           center: [17.250, 53.050] },
      { nameAr: 'حصوين',          nameEn: 'Husaywn',         center: [17.017, 53.600] },
      { nameAr: 'قشن',            nameEn: 'Qishn',           center: [15.417, 51.683] },
      { nameAr: 'الماسنة',        nameEn: "Al Masna'ah",     center: [16.217, 52.433] },
      { nameAr: 'طيبة',           nameEn: 'Taybah',          center: [16.650, 53.350] },
      { nameAr: 'شرورة البادية',  nameEn: 'Shuroor Badiyah', center: [17.700, 52.983] },
      { nameAr: 'سيحوت',          nameEn: 'Sayhut',          center: [15.217, 51.267] },
    ],
  },

  // ─── 13. لحج ─────────────────────────────────────────────────────────────────
  {
    nameAr: 'لحج',
    nameEn: 'Lahij',
    center: [13.050, 44.883],
    districts: [
      { nameAr: 'الحوطة',         nameEn: 'Al Hawtah',       center: [13.058, 44.886] },
      { nameAr: 'تبن',            nameEn: 'Tuban',           center: [12.967, 44.867] },
      { nameAr: 'الحبيلين',       nameEn: 'Al Hubaylene',    center: [13.283, 44.717] },
      { nameAr: 'المسيمير',       nameEn: 'Al Musaymir',     center: [13.267, 44.550] },
      { nameAr: 'الملاح',         nameEn: 'Al Millah',       center: [13.483, 44.750] },
      { nameAr: 'رصد',            nameEn: 'Rasd',            center: [13.383, 44.633] },
      { nameAr: 'القبيطة',        nameEn: 'Al Qubaytah',     center: [13.100, 44.600] },
      { nameAr: 'يافع',           nameEn: "Yafa'",           center: [13.617, 45.100] },
      { nameAr: 'ردفان',          nameEn: 'Radfan',          center: [13.467, 45.000] },
      { nameAr: 'طور الباحة',     nameEn: 'Tur Al Bahah',    center: [13.283, 44.983] },
      { nameAr: 'الشقيرة',        nameEn: 'Ash Shuqayrah',   center: [13.283, 44.433] },
      { nameAr: 'حالمين',         nameEn: 'Halmin',          center: [12.867, 44.733] },
      { nameAr: 'صبيحة',          nameEn: 'Subayhah',        center: [12.900, 44.683] },
      { nameAr: 'كرش',            nameEn: 'Karsh',           center: [13.083, 44.950] },
      { nameAr: 'الحواشب',        nameEn: 'Al Hawashib',     center: [13.200, 44.833] },
      { nameAr: 'خبر',            nameEn: 'Khabb',           center: [13.183, 44.717] },
    ],
  },

  // ─── 14. الضالع ──────────────────────────────────────────────────────────────
  {
    nameAr: 'الضالع',
    nameEn: "Ad Dhali'",
    center: [13.697, 44.730],
    districts: [
      { nameAr: 'الضالع',         nameEn: "Ad Dhali'",       center: [13.697, 44.730] },
      { nameAr: 'جحاف',           nameEn: 'Juban',           center: [13.600, 44.617] },
      { nameAr: 'قعطبة',          nameEn: "Qa'atabah",       center: [13.533, 44.383] },
      { nameAr: 'الأزارق',        nameEn: 'Al Azariq',       center: [13.717, 44.650] },
      { nameAr: 'المسيمير',       nameEn: 'Al Musaymir',     center: [13.567, 44.617] },
      { nameAr: 'دمت',            nameEn: 'Dammt',           center: [14.200, 44.667] },
      { nameAr: 'دار الأهمر',     nameEn: 'Dar Al Ahmar',    center: [13.867, 44.617] },
      { nameAr: 'المقاطرة',       nameEn: 'Al Muqatirah',    center: [13.417, 44.500] },
      { nameAr: 'ريداع',          nameEn: "Rida'",           center: [13.483, 44.717] },
    ],
  },

  // ─── 15. مأرب ────────────────────────────────────────────────────────────────
  {
    nameAr: 'مأرب',
    nameEn: 'Marib',
    center: [15.468, 45.322],
    districts: [
      { nameAr: 'مأرب',           nameEn: 'Marib',           center: [15.468, 45.322] },
      { nameAr: 'رغوان',          nameEn: 'Raghwan',         center: [15.783, 44.967] },
      { nameAr: 'ماهلية',         nameEn: 'Mahliyah',        center: [15.367, 45.133] },
      { nameAr: 'حريب',           nameEn: 'Harib',           center: [15.433, 45.483] },
      { nameAr: 'الجوبة',         nameEn: 'Al Jubah',        center: [15.000, 45.083] },
      { nameAr: 'جور',            nameEn: 'Jawr',            center: [15.183, 45.633] },
      { nameAr: 'مجزر',           nameEn: 'Majzar',          center: [15.617, 45.367] },
      { nameAr: 'الجدعان',        nameEn: "Al Jad'an",       center: [15.283, 45.567] },
      { nameAr: 'الوادي والفلج',  nameEn: 'Al Wadi wal Falaj',center: [15.900, 45.367] },
      { nameAr: 'صرواح',          nameEn: 'Sarwah',          center: [15.383, 44.817] },
      { nameAr: 'بيحان',          nameEn: 'Bayhan',          center: [15.067, 45.733] },
      { nameAr: 'رحبة',           nameEn: 'Rahabah',         center: [15.700, 45.533] },
      { nameAr: 'مأرب مدينة',     nameEn: 'Marib City',      center: [15.472, 45.330] },
      { nameAr: 'حريب القراء',    nameEn: 'Harib Al Qaramis',center: [15.333, 45.383] },
    ],
  },

  // ─── 16. الجوف ───────────────────────────────────────────────────────────────
  {
    nameAr: 'الجوف',
    nameEn: 'Al Jawf',
    center: [16.167, 45.017],
    districts: [
      { nameAr: 'الحزم',          nameEn: 'Al Hazm',         center: [16.167, 45.012] },
      { nameAr: 'الخلق',          nameEn: 'Al Khalaq',       center: [16.300, 45.033] },
      { nameAr: 'برط العنان',     nameEn: 'Bart Al Anan',    center: [16.617, 44.983] },
      { nameAr: 'خب والشعف',      nameEn: "Khabb wa Ash Sha'f", center: [16.367, 44.817] },
      { nameAr: 'المتون',         nameEn: 'Al Mutun',        center: [16.167, 44.983] },
      { nameAr: 'المصلوب',        nameEn: 'Al Maslub',       center: [16.500, 45.583] },
      { nameAr: 'رجوزة',          nameEn: 'Rajuzah',         center: [16.583, 45.350] },
      { nameAr: 'الغيل',          nameEn: 'Al Ghayl',        center: [16.200, 45.733] },
      { nameAr: 'الحياة',         nameEn: 'Al Hayat',        center: [16.067, 44.850] },
      { nameAr: 'العبدية',        nameEn: 'Al Abdiyah',      center: [15.583, 44.800] },
      { nameAr: 'ذهبان',          nameEn: 'Dhahban',         center: [15.750, 44.850] },
    ],
  },

  // ─── 17. صعدة ────────────────────────────────────────────────────────────────
  {
    nameAr: 'صعدة',
    nameEn: "Sa'dah",
    center: [16.933, 43.767],
    districts: [
      { nameAr: 'صعدة',           nameEn: "Sa'dah",          center: [16.938, 43.762] },
      { nameAr: 'سحار',           nameEn: 'Sahar',           center: [17.067, 43.500] },
      { nameAr: 'منبه',           nameEn: 'Munabbih',        center: [17.150, 43.300] },
      { nameAr: 'باقم',           nameEn: 'Baqim',           center: [16.917, 43.317] },
      { nameAr: 'قطابر',          nameEn: 'Qatabir',         center: [17.000, 43.917] },
      { nameAr: 'شداء',           nameEn: 'Shada',           center: [17.083, 43.467] },
      { nameAr: 'مجز',            nameEn: 'Majz',            center: [16.683, 43.867] },
      { nameAr: 'الصفراء',        nameEn: 'As Saffrah',      center: [16.617, 43.600] },
      { nameAr: 'كتاف',           nameEn: 'Kitaf',           center: [16.783, 43.933] },
      { nameAr: 'ميدي',           nameEn: 'Midi',            center: [16.317, 43.100] },
      { nameAr: 'غمر',            nameEn: 'Ghamar',          center: [16.950, 44.083] },
      { nameAr: 'فارع',           nameEn: "Fara'",           center: [16.450, 44.033] },
      { nameAr: 'الزهرة',         nameEn: 'Az Zahrah',       center: [16.650, 43.650] },
      { nameAr: 'حيدان',          nameEn: 'Haydan',          center: [16.983, 43.583] },
      { nameAr: 'السلفية',        nameEn: 'As Salafiyah',    center: [16.500, 43.783] },
    ],
  },

  // ─── 18. حجة ─────────────────────────────────────────────────────────────────
  {
    nameAr: 'حجة',
    nameEn: 'Hajjah',
    center: [15.693, 43.595],
    districts: [
      { nameAr: 'حجة',            nameEn: 'Hajjah',          center: [15.693, 43.595] },
      { nameAr: 'عبس',            nameEn: 'Abs',             center: [15.833, 43.417] },
      { nameAr: 'ميدي',           nameEn: 'Midi',            center: [16.317, 43.100] },
      { nameAr: 'كشر',            nameEn: 'Kushar',          center: [15.783, 43.300] },
      { nameAr: 'مستبأ',          nameEn: 'Mustaba',         center: [15.683, 43.300] },
      { nameAr: 'شرس',            nameEn: 'Shiras',          center: [15.550, 43.833] },
      { nameAr: 'الجماعة',        nameEn: "Al Jama'ah",      center: [15.917, 43.817] },
      { nameAr: 'بكيل المير',     nameEn: 'Bakil Al Mir',    center: [15.717, 43.950] },
      { nameAr: 'قارة',           nameEn: 'Qarah',           center: [16.050, 43.650] },
      { nameAr: 'الشاهل',         nameEn: 'Ash Shahil',      center: [16.167, 43.717] },
      { nameAr: 'كحلان الشرف',    nameEn: 'Kahlan Ash Sharaf',center: [15.433, 43.633] },
      { nameAr: 'خيران المحرق',   nameEn: 'Khayran Al Muhraq',center: [15.533, 43.317] },
      { nameAr: 'حيران',          nameEn: 'Hayran',          center: [16.000, 43.300] },
      { nameAr: 'نجرة',           nameEn: 'Najrah',          center: [15.617, 43.783] },
      { nameAr: 'أفلح اليمن',     nameEn: 'Aflah Al Yaman',  center: [15.867, 43.583] },
      { nameAr: 'أفلح الشام',     nameEn: 'Aflah Ash Sham',  center: [15.967, 43.517] },
      { nameAr: 'المفتاح',        nameEn: 'Al Miftah',       center: [15.267, 43.750] },
      { nameAr: 'مبين',           nameEn: 'Mabyan',          center: [15.383, 43.867] },
      { nameAr: 'الشغادرة',       nameEn: 'Ash Shahadah',    center: [15.817, 43.733] },
      { nameAr: 'كحلان عفار',     nameEn: 'Kahlan Afar',     center: [15.283, 43.767] },
      { nameAr: 'واقر',           nameEn: 'Waqr',            center: [16.167, 43.933] },
      { nameAr: 'ملحان',          nameEn: 'Milhan',          center: [15.367, 43.500] },
      { nameAr: 'المغربة',        nameEn: 'Al Magharabah',   center: [15.133, 43.583] },
      { nameAr: 'الجبين',         nameEn: 'Al Jubayn',       center: [15.650, 43.783] },
      { nameAr: 'ريدة',           nameEn: 'Rida',            center: [15.967, 43.700] },
      { nameAr: 'الزهراء',        nameEn: 'Az Zahrah',       center: [15.900, 43.700] },
      { nameAr: 'خولان',          nameEn: 'Khawlan',         center: [16.100, 43.800] },
      { nameAr: 'عقيب الأشاريش', nameEn: 'Uqayb Al Asharish',center: [16.083, 43.883] },
      { nameAr: 'القفلة وعيال يزيد',nameEn: 'Al Quflah',    center: [15.383, 43.583] },
      { nameAr: 'القبلة',         nameEn: 'Al Qiblah',       center: [15.283, 43.617] },
      { nameAr: 'وادي الوداي',    nameEn: 'Wadi Al Waday',   center: [15.733, 43.683] },
    ],
  },

  // ─── 19. عمران ───────────────────────────────────────────────────────────────
  {
    nameAr: 'عمران',
    nameEn: 'Amran',
    center: [15.659, 43.944],
    districts: [
      { nameAr: 'عمران',          nameEn: 'Amran',           center: [15.659, 43.944] },
      { nameAr: 'حرف سفيان',      nameEn: 'Harf Sufyan',     center: [15.900, 43.783] },
      { nameAr: 'الأحنوم',        nameEn: 'Al Ahnoom',       center: [16.133, 44.133] },
      { nameAr: 'خارف',           nameEn: 'Kharef',          center: [16.017, 44.083] },
      { nameAr: 'ثلا',            nameEn: 'Thulah',          center: [15.583, 44.167] },
      { nameAr: 'العمشية',        nameEn: 'Al Amashiyah',    center: [15.450, 43.767] },
      { nameAr: 'ريدة',           nameEn: 'Raydah',          center: [15.967, 43.750] },
      { nameAr: 'عيال سريح',      nameEn: 'Ayal Surayh',     center: [15.683, 43.733] },
      { nameAr: 'يام',            nameEn: 'Yam',             center: [16.300, 44.283] },
      { nameAr: 'قفل شمر',        nameEn: 'Qafal Shamir',    center: [16.200, 44.533] },
      { nameAr: 'مسور',           nameEn: 'Maswar',          center: [15.533, 44.117] },
      { nameAr: 'الحشا',          nameEn: 'Al Hasha',        center: [15.767, 43.867] },
      { nameAr: 'السودة',         nameEn: 'As Sawdah',       center: [15.450, 44.017] },
      { nameAr: 'جبل أسود',       nameEn: 'Jabal Aswad',     center: [15.883, 44.183] },
      { nameAr: 'بني عصام',       nameEn: 'Bani Usamah',     center: [15.600, 43.867] },
      { nameAr: 'القابل',         nameEn: 'Al Qabil',        center: [16.150, 44.367] },
      { nameAr: 'الأسد',          nameEn: 'Al Asad',         center: [15.733, 44.000] },
      { nameAr: 'المحابشة',       nameEn: 'Al Mahaqashah',   center: [15.533, 43.833] },
      { nameAr: 'سنحان',          nameEn: 'Sanhan',          center: [15.183, 44.267] },
      { nameAr: 'الأصبوحي',       nameEn: 'Al Asbahi',       center: [15.817, 44.133] },
    ],
  },

  // ─── 20. المحويت ─────────────────────────────────────────────────────────────
  {
    nameAr: 'المحويت',
    nameEn: 'Al Mahwit',
    center: [15.468, 43.571],
    districts: [
      { nameAr: 'المحويت',        nameEn: 'Al Mahwit',       center: [15.468, 43.571] },
      { nameAr: 'شبام كوكبان',    nameEn: 'Shibam Kawkaban', center: [15.433, 43.633] },
      { nameAr: 'ملحان',          nameEn: 'Milhan',          center: [15.367, 43.500] },
      { nameAr: 'حفاش',           nameEn: 'Hufash',          center: [15.283, 43.433] },
      { nameAr: 'مذبة',           nameEn: 'Madhbah',         center: [15.567, 43.617] },
      { nameAr: 'الطفة',          nameEn: 'At Taffah',       center: [15.317, 43.617] },
      { nameAr: 'الراجز',         nameEn: 'Ar Rajiz',        center: [15.600, 43.683] },
      { nameAr: 'سهل بني هاشم',   nameEn: 'Sahl Bani Hashim',center: [15.200, 43.617] },
      { nameAr: 'بني سعد',        nameEn: "Bani Sa'd",       center: [15.350, 43.500] },
      { nameAr: 'كحلان الشرف',    nameEn: 'Kahlan Ash Sharaf',center: [15.433, 43.633] },
    ],
  },

  // ─── 21. ريمة ────────────────────────────────────────────────────────────────
  {
    nameAr: 'ريمة',
    nameEn: 'Raymah',
    center: [14.633, 43.700],
    districts: [
      { nameAr: 'الجبين',         nameEn: 'Al Jubayn',       center: [14.683, 43.700] },
      { nameAr: 'بلاد الطعام',    nameEn: 'Bilad Al Ta\'am', center: [14.817, 43.600] },
      { nameAr: 'كسمة',           nameEn: 'Kusmah',          center: [14.517, 43.600] },
      { nameAr: 'الجعفرية',       nameEn: 'Al Ja\'fariyah',  center: [14.633, 43.833] },
      { nameAr: 'السدة',          nameEn: 'As Saddah',       center: [14.500, 43.733] },
      { nameAr: 'المزاحم',        nameEn: 'Al Muzahim',      center: [14.700, 43.617] },
      { nameAr: 'المسنة',         nameEn: 'Al Masnah',       center: [14.567, 43.567] },
    ],
  },

  // ─── 22. سقطرى ───────────────────────────────────────────────────────────────
  {
    nameAr: 'سقطرى',
    nameEn: 'Socotra',
    center: [12.506, 53.919],
    districts: [
      { nameAr: 'حديبو',              nameEn: 'Hadibo',              center: [12.634, 54.026] },
      { nameAr: 'قلنسية وعبد الكوري', nameEn: 'Qalansiyah wa Abd Al Kuri', center: [12.683, 53.483] },
      { nameAr: 'نوجد',               nameEn: 'Nojd',                center: [12.400, 53.833] },
      { nameAr: 'سقطرى الوسطى',       nameEn: 'Socotra Central',     center: [12.506, 53.919] },
    ],
  },
];
