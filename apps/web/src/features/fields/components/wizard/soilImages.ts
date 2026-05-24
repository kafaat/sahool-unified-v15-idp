/**
 * Maps soil types to descriptive colors and labels.
 * Real soil texture photos would be placed at /public/images/soil/{type}.jpg
 * Using CSS gradient placeholders so the step works without external assets.
 */

export interface SoilVisual {
  /** CSS gradient string for the preview swatch */
  gradient: string;
  /** Hex accent color for border */
  color: string;
  /** Short Arabic description */
  descAr: string;
  /** Short English description */
  descEn: string;
}

export const SOIL_VISUALS: Record<string, SoilVisual> = {
  clay: {
    gradient: 'linear-gradient(135deg, #8B4513 0%, #A0522D 40%, #CD853F 100%)',
    color: '#8B4513',
    descAr: 'تربة طينية ثقيلة، تحتفظ بالرطوبة جيداً، مناسبة لمحاصيل الأرز والقمح.',
    descEn: 'Heavy clay soil. Retains moisture well. Suitable for rice and wheat.',
  },
  sandy: {
    gradient: 'linear-gradient(135deg, #F4D03F 0%, #E8C547 40%, #D4A017 100%)',
    color: '#D4A017',
    descAr: 'تربة رملية خفيفة، صرف سريع، مناسبة للبطيخ والبطاطس والجزر.',
    descEn: 'Light sandy soil. Fast-draining. Suitable for watermelon, potato, carrot.',
  },
  loamy: {
    gradient: 'linear-gradient(135deg, #6B4226 0%, #8B6340 40%, #A0785A 100%)',
    color: '#6B4226',
    descAr: 'تربة طمية متوازنة، مثالية لمعظم المحاصيل الزراعية.',
    descEn: 'Balanced loamy soil. Ideal for most crops.',
  },
  silty: {
    gradient: 'linear-gradient(135deg, #B8936A 0%, #C9A882 40%, #D4B896 100%)',
    color: '#B8936A',
    descAr: 'تربة غرينية ناعمة، خصبة، مناسبة للخضروات والمحاصيل الحقلية.',
    descEn: 'Fine silty soil. Fertile. Suitable for vegetables and field crops.',
  },
  saline: {
    gradient: 'linear-gradient(135deg, #B0C4DE 0%, #C0D0E8 40%, #D0E0F0 100%)',
    color: '#607080',
    descAr: 'تربة ملحية، تحتاج إلى غسيل وصرف جيد، مناسبة للمحاصيل المقاومة للملوحة.',
    descEn: 'Saline soil. Requires leaching and good drainage. Suitable for salt-tolerant crops.',
  },
};

export const SOIL_OPTIONS = [
  { value: 'clay',   labelAr: 'طيني',             labelEn: 'Clay' },
  { value: 'sandy',  labelAr: 'رملي',             labelEn: 'Sandy' },
  { value: 'loamy',  labelAr: 'طمي (مزيجي)',      labelEn: 'Loamy' },
  { value: 'silty',  labelAr: 'غريني',            labelEn: 'Silty' },
  { value: 'saline', labelAr: 'ملحي',             labelEn: 'Saline' },
];
