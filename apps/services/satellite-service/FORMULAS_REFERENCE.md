# Vegetation Indices Formulas Reference

## Complete Technical Reference

All formulas use Sentinel-2 MSI band reflectance values (0-1 scale).

---

## Sentinel-2 Band Definitions

| Variable | Band | Name            | Wavelength | Resolution |
| -------- | ---- | --------------- | ---------- | ---------- |
| Blue     | B02  | Blue            | 490 nm     | 10 m       |
| Green    | B03  | Green           | 560 nm     | 10 m       |
| Red      | B04  | Red             | 665 nm     | 10 m       |
| RE1      | B05  | Red Edge 1      | 705 nm     | 20 m       |
| RE2      | B06  | Red Edge 2      | 740 nm     | 20 m       |
| RE3      | B07  | Red Edge 3      | 783 nm     | 20 m       |
| NIR      | B08  | Near Infrared   | 842 nm     | 10 m       |
| NIRn     | B8A  | NIR Narrow      | 865 nm     | 20 m       |
| SWIR1    | B11  | Short Wave IR 1 | 1610 nm    | 20 m       |
| SWIR2    | B12  | Short Wave IR 2 | 2190 nm    | 20 m       |

---

## Basic Indices

### 1. NDVI - Normalized Difference Vegetation Index

```
NDVI = (NIR - Red) / (NIR + Red)
```

**Range:** -1 to 1 (vegetation: 0.2 to 0.9)
**Interpretation:**

- > 0.7: Dense vegetation
- 0.5-0.7: Moderate vegetation
- 0.2-0.5: Sparse vegetation
- < 0.2: Bare soil/water

**Best for:** Overall vegetation health, biomass estimation

---

### 2. NDWI - Normalized Difference Water Index

```
NDWI = (NIR - SWIR1) / (NIR + SWIR1)
```

**Range:** -1 to 1
**Interpretation:**

- > 0.2: No water stress
- 0.0 to 0.2: Mild water stress
- -0.1 to 0.0: Moderate water stress
- < -0.2: Severe water stress

**Best for:** Water content monitoring, irrigation scheduling

---

### 3. EVI - Enhanced Vegetation Index

```
EVI = 2.5 × (NIR - Red) / (NIR + 6×Red - 7.5×Blue + 1)
```

**Range:** -1 to 1 (vegetation: 0.2 to 0.8)
**Coefficients:**

- G = 2.5 (gain factor)
- C1 = 6 (aerosol resistance coefficient for red)
- C2 = 7.5 (aerosol resistance coefficient for blue)
- L = 1 (canopy background adjustment)

**Best for:** High biomass areas, atmospheric correction

---

### 4. SAVI - Soil Adjusted Vegetation Index

```
SAVI = ((NIR - Red) / (NIR + Red + L)) × (1 + L)
```

**Where:** L = soil brightness correction factor
**Standard L values:**

- L = 0.25: High vegetation cover
- L = 0.5: Intermediate vegetation (default)
- L = 1.0: Low vegetation cover

**Range:** -1 to 1
**Best for:** Areas with exposed soil, sparse vegetation

---

### 5. LAI - Leaf Area Index

```
LAI = 3.618 × exp(2.907 × NDVI) - 3.618
```

**Constraint:** NDVI capped at 0.68 to avoid unrealistic values
**Range:** 0 to 8+ (typical crops: 1 to 6)
**Interpretation:**

- > 4: Full canopy
- 2.5-4: Good leaf coverage
- 1.5-2.5: Moderate coverage
- < 1.5: Sparse coverage

**Best for:** Canopy development monitoring

---

### 6. NDMI - Normalized Difference Moisture Index

```
NDMI = (NIR - SWIR1) / (NIR + SWIR1)
```

**Note:** Same formula as NDWI, different interpretation context
**Range:** -1 to 1
**Best for:** Vegetation moisture content, drought stress

---

## Chlorophyll & Nitrogen Indices

### 7. NDRE - Normalized Difference Red Edge

```
NDRE = (NIR - RE1) / (NIR + RE1)
```

**Range:** -1 to 1 (typical: 0.2 to 0.7)
**Interpretation:**

- > 0.35: Excellent chlorophyll (sufficient nitrogen)
- 0.25-0.35: Good chlorophyll
- 0.15-0.25: Fair (consider nitrogen)
- < 0.15: Low chlorophyll (nitrogen needed)

**Best for:** Mid-season nitrogen status, chlorophyll content

---

### 8. CVI - Chlorophyll Vegetation Index

```
CVI = NIR × (Red / Green²)
```

**Range:** 0 to 10+ (typical: 1 to 5)
**Best for:** Chlorophyll content assessment

---

### 9. MCARI - Modified Chlorophyll Absorption Ratio Index

```
MCARI = [(RE1 - Red) - 0.2 × (RE1 - Green)] × (RE1 / Red)
```

**Range:** 0 to 1.5 (higher = more chlorophyll)
**Interpretation:**

- > 0.6: High chlorophyll
- 0.3-0.6: Moderate chlorophyll
- < 0.3: Low chlorophyll

**Best for:** Chlorophyll concentration in crops

---

### 10. TCARI - Transformed Chlorophyll Absorption Ratio Index

```
TCARI = 3 × [(RE1 - Red) - 0.2 × (RE1 - Green) × (RE1/Red)]
```

**Range:** 0 to 3 (typical: 0.5 to 2)
**Best for:** Chlorophyll content, resistant to LAI effects

---

### 11. SIPI - Structure Insensitive Pigment Index

```
SIPI = (NIR - Blue) / (NIR - Red)
```

**Range:** 0 to 2 (typical: 0.8 to 1.8)
**Interpretation:**

- < 1: High carotenoid/chlorophyll ratio (stress)
- ≈ 1: Normal pigment ratio
- > 1: Low carotenoid/chlorophyll ratio (healthy)

**Best for:** Carotenoid to chlorophyll ratio, early stress

---

## Early Stress Detection Indices

### 12. GNDVI - Green Normalized Difference Vegetation Index

```
GNDVI = (NIR - Green) / (NIR + Green)
```

**Range:** -1 to 1 (typical: 0.3 to 0.8)
**Interpretation:**

- > 0.6: Excellent photosynthetic activity
- 0.45-0.6: Good activity
- 0.3-0.45: Fair (early stress signs)
- < 0.3: Poor (stress detected)

**Best for:** Early nitrogen stress, more sensitive than NDVI in early stages

---

### 13. VARI - Visible Atmospherically Resistant Index

```
VARI = (Green - Red) / (Green + Red - Blue)
```

**Range:** -1 to 1 (typical: 0 to 1)
**Best for:** Early season when canopy not fully developed

---

### 14. GLI - Green Leaf Index

```
GLI = (2×Green - Red - Blue) / (2×Green + Red + Blue)
```

**Range:** -1 to 1 (typical: -0.5 to 0.5)
**Interpretation:**

- > 0.2: High green biomass
- 0 to 0.2: Moderate green biomass
- < 0: Low green biomass

**Best for:** Green biomass monitoring, early growth

---

### 15. GRVI - Green-Red Vegetation Index

```
GRVI = (Green - Red) / (Green + Red)
```

**Range:** -1 to 1 (typical: -0.5 to 0.5)
**Best for:** Vegetation detection in visible spectrum

---

## Soil & Atmosphere Corrected Indices

### 16. MSAVI - Modified Soil Adjusted Vegetation Index

```
MSAVI = (2×NIR + 1 - √[(2×NIR+1)² - 8×(NIR-Red)]) / 2
```

**Derivation:**

```
a = 2×NIR + 1
b = a²
c = 8×(NIR - Red)
MSAVI = (a - √(b - c)) / 2
```

**Range:** -1 to 1 (typical: 0.2 to 0.8)
**Best for:** Sparse vegetation, minimizes soil background

---

### 17. OSAVI - Optimized Soil Adjusted Vegetation Index

```
OSAVI = (NIR - Red) / (NIR + Red + Y)

where Y = 0.16 (optimized constant)
```

**Range:** -1 to 1 (typical: 0.2 to 0.8)
**Best for:** Intermediate vegetation cover

---

### 18. ARVI - Atmospherically Resistant Vegetation Index

```
ARVI = (NIR - RB) / (NIR + RB)

where RB = 2×Red - Blue (red-blue term)
```

**Expanded form:**

```
ARVI = (NIR - (2×Red - Blue)) / (NIR + (2×Red - Blue))
```

**Range:** -1 to 1 (typical: 0.2 to 0.8)
**Best for:** Reducing atmospheric aerosol effects

---

## Practical Implementation Notes

### Error Handling

**Division by Zero:**

```python
if denominator == 0:
    return 0.0
```

**Value Clamping:**

```python
# Clamp to valid range
value = max(-1, min(value, 1))
```

### Rounding

All indices rounded to 4 decimal places:

```python
return round(value, 4)
```

LAI rounded to 2 decimal places:

```python
return round(lai, 2)
```

---

## Validation Formulas

### Cross-Validation

**NDVI vs EVI Relationship:**

```
EVI ≈ 0.7 × NDVI  (approximate for healthy vegetation)
```

**NDWI vs NDMI Relationship:**

```
NDWI ≈ NDMI  (same formula, different applications)
```

**LAI vs NDVI Relationship:**

```
LAI increases exponentially with NDVI
At NDVI=0.5: LAI ≈ 2.5
At NDVI=0.7: LAI ≈ 4.5
```

---

## Common Combinations

### Nitrogen Assessment

```python
if NDRE < 0.25 and GNDVI < 0.45:
    # Strong evidence of nitrogen deficiency
    recommendation = "Apply nitrogen fertilizer"
```

### Water Stress Detection

```python
if NDWI < 0 and NDMI < 0:
    # Both water indices show stress
    recommendation = "Immediate irrigation required"
```

### Overall Health

```python
health_score = (
    0.4 × normalize(NDVI) +
    0.2 × normalize(NDRE) +
    0.2 × normalize(NDWI) +
    0.2 × normalize(EVI)
)
```

---

## References

1. Rouse, J.W., et al. (1974). "Monitoring vegetation systems in the Great Plains with ERTS." _NASA SP-351_.

2. Gao, B. (1996). "NDWI - A normalized difference water index for remote sensing of vegetation liquid water from space." _Remote Sensing of Environment_, 58(3), 257-266.

3. Huete, A., et al. (2002). "Overview of the radiometric and biophysical performance of the MODIS vegetation indices." _Remote Sensing of Environment_, 83(1-2), 195-213.

4. Gitelson, A.A., et al. (2005). "Remote estimation of chlorophyll content in higher plant leaves." _International Journal of Remote Sensing_, 18(12), 2691-2697.

5. ESA (2015). "Sentinel-2 User Handbook." European Space Agency.

---

**Document Version:** 1.0
**Last Updated:** December 2025
**SAHOOL Satellite Service v15.7.0**
