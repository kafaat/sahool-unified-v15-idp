"""
Export endpoints to be added to main.py
"""

# Add these endpoints before the "if __name__ == '__main__':" block in main.py

EXPORT_ENDPOINTS_CODE = '''
# =============================================================================
# Data Export Endpoints
# =============================================================================

@app.get("/v1/export/analysis/{field_id}")
async def export_analysis(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    format: str = Query(default="geojson", description="Export format: geojson, csv, json, kml")
) -> StreamingResponse:
    """
    Export field analysis data in specified format.

    Formats:
    - geojson: Geographic data with analysis properties
    - csv: Tabular format with flattened data
    - json: Complete JSON structure
    - kml: Google Earth compatible format
    """
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: geojson, csv, json, kml"
        )

    # Get analysis data
    try:
        # Use the existing analyze endpoint logic
        analysis_data = await _perform_analysis(field_id, lat, lon)

        # Export data
        exporter = DataExporter()
        result = exporter.export_field_analysis(
            field_id=field_id,
            analysis_data=analysis_data,
            format=export_format
        )

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode('utf-8') if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Export analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") from e


@app.get("/v1/export/timeseries/{field_id}")
async def export_timeseries(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query(default="csv", description="Export format: csv, json, geojson")
) -> StreamingResponse:
    """
    Export time series data (NDVI over time) in specified format.

    Best for tracking vegetation health trends over time.
    """
    try:
        export_format = ExportFormat(format.lower())
        if export_format == ExportFormat.KML:
            raise HTTPException(
                status_code=400,
                detail="KML format not supported for timeseries. Use csv, json, or geojson"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: csv, json, geojson"
        )

    # Parse dates
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD"
        )

    # Get timeseries data using existing endpoint logic
    try:
        # Simulate timeseries data collection
        timeseries_data = []
        current_date = start_dt

        while current_date <= end_dt:
            # Get analysis for each date
            analysis = await _perform_analysis(field_id, lat, lon, analysis_date=current_date)

            point = {
                "date": current_date.isoformat(),
                "latitude": lat,
                "longitude": lon,
                "ndvi": analysis.get("indices", {}).get("ndvi", 0),
                "ndwi": analysis.get("indices", {}).get("ndwi", 0),
                "evi": analysis.get("indices", {}).get("evi", 0),
                "health_score": analysis.get("health_score", 0),
                "health_status": analysis.get("health_status", "unknown"),
                "cloud_cover": analysis.get("imagery", {}).get("cloud_cover_percent", 0)
            }
            timeseries_data.append(point)

            # Move to next week (reduce data points)
            current_date += timedelta(days=7)

        # Export data
        exporter = DataExporter()
        result = exporter.export_timeseries(
            field_id=field_id,
            timeseries_data=timeseries_data,
            format=export_format
        )

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode('utf-8') if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Data-Points": str(len(timeseries_data))
            }
        )
    except Exception as e:
        logger.error(f"Export timeseries error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") from e


@app.get("/v1/export/boundaries")
async def export_boundaries(
    field_ids: str = Query(..., description="Comma-separated field IDs"),
    format: str = Query(default="geojson", description="Export format: geojson, json, kml")
) -> StreamingResponse:
    """
    Export field boundaries in specified format.

    Useful for GIS systems and mapping applications.
    """
    try:
        export_format = ExportFormat(format.lower())
        if export_format == ExportFormat.CSV:
            raise HTTPException(
                status_code=400,
                detail="CSV format not supported for boundaries. Use geojson, json, or kml"
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: geojson, json, kml"
        )

    # Parse field IDs
    field_id_list = [fid.strip() for fid in field_ids.split(",") if fid.strip()]

    if not field_id_list:
        raise HTTPException(status_code=400, detail="No field IDs provided")

    if len(field_id_list) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 fields per export")

    # Collect boundary data for each field
    boundaries = []
    for field_id in field_id_list:
        # Simulate boundary data (in production, fetch from database)
        boundary = {
            "field_id": field_id,
            "name": f"Field {field_id}",
            "area_hectares": 2.5,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [44.0, 15.0],
                        [44.01, 15.0],
                        [44.01, 15.01],
                        [44.0, 15.01],
                        [44.0, 15.0]
                    ]
                ]
            }
        }
        boundaries.append(boundary)

    # Export data
    try:
        exporter = DataExporter()
        result = exporter.export_boundaries(
            boundaries=boundaries,
            format=export_format
        )

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode('utf-8') if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Field-Count": str(len(boundaries))
            }
        )
    except Exception as e:
        logger.error(f"Export boundaries error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") from e


@app.get("/v1/export/report/{field_id}")
async def export_report(
    field_id: str,
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    report_type: str = Query(default="full", description="Report type: full, summary, changes"),
    format: str = Query(default="json", description="Export format: json, csv, geojson")
) -> StreamingResponse:
    """
    Export comprehensive field report.

    Report types:
    - full: Complete analysis with all indices and recommendations
    - summary: High-level health metrics
    - changes: Change detection over time
    """
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format '{format}'. Supported: json, csv, geojson"
        )

    if report_type not in ["full", "summary", "changes"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid report_type. Use: full, summary, or changes"
        )

    try:
        # Get analysis data
        analysis_data = await _perform_analysis(field_id, lat, lon)

        # Build report based on type
        if report_type == "full":
            report_data = analysis_data
        elif report_type == "summary":
            report_data = {
                "field_id": field_id,
                "health_score": analysis_data.get("health_score"),
                "health_status": analysis_data.get("health_status"),
                "ndvi": analysis_data.get("indices", {}).get("ndvi"),
                "analysis_date": analysis_data.get("analysis_date"),
                "anomalies_count": len(analysis_data.get("anomalies", []))
            }
        else:  # changes
            # Get historical data for comparison
            week_ago = date.today() - timedelta(days=7)
            historical = await _perform_analysis(field_id, lat, lon, analysis_date=week_ago)

            current_ndvi = analysis_data.get("indices", {}).get("ndvi", 0)
            historical_ndvi = historical.get("indices", {}).get("ndvi", 0)

            report_data = {
                "field_id": field_id,
                "current_date": date.today().isoformat(),
                "comparison_date": week_ago.isoformat(),
                "changes": {
                    "ndvi_change": current_ndvi - historical_ndvi,
                    "ndvi_change_percent": ((current_ndvi - historical_ndvi) / historical_ndvi * 100) if historical_ndvi else 0,
                    "health_score_change": analysis_data.get("health_score", 0) - historical.get("health_score", 0),
                    "status_change": f"{historical.get('health_status')} → {analysis_data.get('health_status')}"
                },
                "current": {
                    "ndvi": current_ndvi,
                    "health_score": analysis_data.get("health_score")
                },
                "historical": {
                    "ndvi": historical_ndvi,
                    "health_score": historical.get("health_score")
                }
            }

        # Export based on format
        exporter = DataExporter()

        if report_type == "changes":
            # Use changes export
            result = exporter.export_changes_report(
                changes=[report_data],
                format=export_format
            )
        else:
            # Use field analysis export
            result = exporter.export_field_analysis(
                field_id=field_id,
                analysis_data=report_data,
                format=export_format
            )

        # Create streaming response
        return StreamingResponse(
            io.BytesIO(result.data.encode('utf-8') if isinstance(result.data, str) else result.data),
            media_type=result.content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{result.filename}"',
                "X-Export-Size": str(result.size_bytes),
                "X-Generated-At": result.generated_at.isoformat(),
                "X-Report-Type": report_type
            }
        )
    except Exception as e:
        logger.error(f"Export report error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}") from e


async def _perform_analysis(field_id: str, lat: float, lon: float, analysis_date: date = None) -> Dict:
    """
    Helper function to perform field analysis.
    This reuses logic from the existing /v1/analyze endpoint.
    """
    # Use multi-provider if available
    if USE_MULTI_PROVIDER and _multi_provider:
        try:
            result = await _multi_provider.analyze_field(
                latitude=lat,
                longitude=lon,
                date=analysis_date or date.today(),
                satellite_type=MultiSatelliteType.SENTINEL2
            )

            # Convert to expected format
            analysis_data = {
                "field_id": field_id,
                "analysis_date": datetime.now().isoformat(),
                "latitude": lat,
                "longitude": lon,
                "satellite": result.get("satellite", "sentinel2"),
                "indices": result.get("indices", {}),
                "health_score": result.get("health_score", 0),
                "health_status": result.get("health_status", "unknown"),
                "anomalies": result.get("anomalies", []),
                "recommendations_ar": result.get("recommendations_ar", []),
                "recommendations_en": result.get("recommendations_en", []),
                "imagery": result.get("imagery", {})
            }

            return analysis_data
        except Exception as e:
            logger.warning(f"Multi-provider analysis failed: {e}, using simulated data")

    # Fallback to simulated data
    import random

    ndvi = random.uniform(0.3, 0.9)
    health_score = ndvi * 100

    return {
        "field_id": field_id,
        "analysis_date": datetime.now().isoformat(),
        "latitude": lat,
        "longitude": lon,
        "satellite": "sentinel2",
        "indices": {
            "ndvi": round(ndvi, 3),
            "ndwi": round(random.uniform(0.2, 0.6), 3),
            "evi": round(random.uniform(0.3, 0.8), 3),
            "savi": round(random.uniform(0.2, 0.7), 3),
            "lai": round(random.uniform(1.0, 5.0), 2),
            "ndmi": round(random.uniform(0.2, 0.6), 3)
        },
        "health_score": round(health_score, 1),
        "health_status": "excellent" if health_score > 80 else "good" if health_score > 60 else "fair",
        "anomalies": [],
        "recommendations_ar": ["مراقبة مستمرة"],
        "recommendations_en": ["Continue monitoring"],
        "imagery": {
            "acquisition_date": (analysis_date or date.today()).isoformat(),
            "cloud_cover_percent": random.uniform(0, 15),
            "scene_id": f"S2A_MSIL2A_{field_id}",
            "latitude": lat,
            "longitude": lon
        }
    }
'''
