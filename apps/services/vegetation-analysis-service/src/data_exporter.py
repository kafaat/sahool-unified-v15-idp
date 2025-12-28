"""
SAHOOL Data Exporter
Export satellite analysis data in various formats (GeoJSON, CSV, JSON, KML)
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Union, Any
from datetime import datetime, date
from enum import Enum
import json
import io
import csv
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


class ExportFormat(Enum):
    GEOJSON = "geojson"
    CSV = "csv"
    JSON = "json"
    KML = "kml"


@dataclass
class ExportResult:
    format: ExportFormat
    filename: str
    content_type: str
    data: Union[str, bytes]
    size_bytes: int
    generated_at: datetime


class DataExporter:
    """
    Export satellite analysis data in various formats.
    """

    CONTENT_TYPES = {
        ExportFormat.GEOJSON: "application/geo+json",
        ExportFormat.CSV: "text/csv",
        ExportFormat.JSON: "application/json",
        ExportFormat.KML: "application/vnd.google-earth.kml+xml",
    }

    def export_field_analysis(
        self,
        field_id: str,
        analysis_data: Dict,
        format: ExportFormat = ExportFormat.GEOJSON
    ) -> ExportResult:
        """
        Export field analysis (NDVI, health, etc.) in specified format.

        Args:
            field_id: Field identifier
            analysis_data: Analysis results containing indices, health score, etc.
            format: Export format

        Returns:
            ExportResult with formatted data
        """
        if format == ExportFormat.GEOJSON:
            data = self._to_geojson(analysis_data, geometry_type="Point")
        elif format == ExportFormat.CSV:
            # Flatten analysis data for CSV
            flat_data = self._flatten_analysis_for_csv(analysis_data)
            data = self._to_csv([flat_data])
        elif format == ExportFormat.JSON:
            data = json.dumps(analysis_data, indent=2, default=str)
        elif format == ExportFormat.KML:
            data = self._to_kml(analysis_data, name=f"Field Analysis {field_id}")
        else:
            raise ValueError(f"Unsupported format: {format}")

        filename = self.generate_filename("field_analysis", field_id, format)

        return ExportResult(
            format=format,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            data=data,
            size_bytes=len(data.encode('utf-8')) if isinstance(data, str) else len(data),
            generated_at=datetime.now()
        )

    def export_timeseries(
        self,
        field_id: str,
        timeseries_data: List[Dict],
        format: ExportFormat = ExportFormat.CSV
    ) -> ExportResult:
        """
        Export time series data (NDVI over time).

        Args:
            field_id: Field identifier
            timeseries_data: List of time series data points
            format: Export format

        Returns:
            ExportResult with formatted data
        """
        if format == ExportFormat.CSV:
            data = self._to_csv(timeseries_data)
        elif format == ExportFormat.JSON:
            data = json.dumps({
                "field_id": field_id,
                "timeseries": timeseries_data,
                "count": len(timeseries_data)
            }, indent=2, default=str)
        elif format == ExportFormat.GEOJSON:
            # Create a FeatureCollection with time series points
            features = []
            for point in timeseries_data:
                if "latitude" in point and "longitude" in point:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [point["longitude"], point["latitude"]]
                        },
                        "properties": {k: v for k, v in point.items()
                                     if k not in ["latitude", "longitude"]}
                    }
                    features.append(feature)

            geojson = {
                "type": "FeatureCollection",
                "features": features,
                "properties": {
                    "field_id": field_id,
                    "count": len(features),
                    "generated_at": datetime.now().isoformat()
                }
            }
            data = json.dumps(geojson, indent=2)
        else:
            raise ValueError(f"Format {format} not supported for timeseries")

        filename = self.generate_filename("timeseries", field_id, format)

        return ExportResult(
            format=format,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            data=data,
            size_bytes=len(data.encode('utf-8')) if isinstance(data, str) else len(data),
            generated_at=datetime.now()
        )

    def export_boundaries(
        self,
        boundaries: List[Dict],
        format: ExportFormat = ExportFormat.GEOJSON
    ) -> ExportResult:
        """
        Export field boundaries as GeoJSON or KML.

        Args:
            boundaries: List of boundary data with coordinates
            format: Export format (GEOJSON or KML)

        Returns:
            ExportResult with formatted data
        """
        if format == ExportFormat.GEOJSON:
            features = []
            for boundary in boundaries:
                feature = {
                    "type": "Feature",
                    "geometry": boundary.get("geometry", {
                        "type": "Polygon",
                        "coordinates": boundary.get("coordinates", [])
                    }),
                    "properties": {
                        k: v for k, v in boundary.items()
                        if k not in ["geometry", "coordinates"]
                    }
                }
                features.append(feature)

            geojson = {
                "type": "FeatureCollection",
                "features": features,
                "properties": {
                    "count": len(features),
                    "generated_at": datetime.now().isoformat()
                }
            }
            data = json.dumps(geojson, indent=2)

        elif format == ExportFormat.KML:
            data = self._boundaries_to_kml(boundaries)

        elif format == ExportFormat.JSON:
            data = json.dumps({
                "boundaries": boundaries,
                "count": len(boundaries),
                "generated_at": datetime.now().isoformat()
            }, indent=2, default=str)
        else:
            raise ValueError(f"Format {format} not supported for boundaries")

        filename = self.generate_filename("boundaries", "multi", format)

        return ExportResult(
            format=format,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            data=data,
            size_bytes=len(data.encode('utf-8')) if isinstance(data, str) else len(data),
            generated_at=datetime.now()
        )

    def export_yield_prediction(
        self,
        prediction_data: Dict,
        format: ExportFormat = ExportFormat.JSON
    ) -> ExportResult:
        """
        Export yield prediction results.

        Args:
            prediction_data: Yield prediction data
            format: Export format

        Returns:
            ExportResult with formatted data
        """
        field_id = prediction_data.get("field_id", "unknown")

        if format == ExportFormat.JSON:
            data = json.dumps(prediction_data, indent=2, default=str)
        elif format == ExportFormat.CSV:
            # Flatten prediction data for CSV
            flat_data = self._flatten_prediction_for_csv(prediction_data)
            data = self._to_csv([flat_data])
        elif format == ExportFormat.GEOJSON:
            data = self._to_geojson(prediction_data, geometry_type="Point")
        else:
            raise ValueError(f"Format {format} not supported for yield prediction")

        filename = self.generate_filename("yield_prediction", field_id, format)

        return ExportResult(
            format=format,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            data=data,
            size_bytes=len(data.encode('utf-8')) if isinstance(data, str) else len(data),
            generated_at=datetime.now()
        )

    def export_changes_report(
        self,
        changes: List[Dict],
        format: ExportFormat = ExportFormat.CSV
    ) -> ExportResult:
        """
        Export change detection report.

        Args:
            changes: List of detected changes
            format: Export format

        Returns:
            ExportResult with formatted data
        """
        if format == ExportFormat.CSV:
            data = self._to_csv(changes)
        elif format == ExportFormat.JSON:
            data = json.dumps({
                "changes": changes,
                "count": len(changes),
                "generated_at": datetime.now().isoformat()
            }, indent=2, default=str)
        elif format == ExportFormat.GEOJSON:
            features = []
            for change in changes:
                if "latitude" in change and "longitude" in change:
                    feature = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [change["longitude"], change["latitude"]]
                        },
                        "properties": {k: v for k, v in change.items()
                                     if k not in ["latitude", "longitude"]}
                    }
                    features.append(feature)

            geojson = {
                "type": "FeatureCollection",
                "features": features,
                "properties": {
                    "count": len(features),
                    "generated_at": datetime.now().isoformat()
                }
            }
            data = json.dumps(geojson, indent=2)
        else:
            raise ValueError(f"Format {format} not supported for changes report")

        filename = self.generate_filename("changes_report", "multi", format)

        return ExportResult(
            format=format,
            filename=filename,
            content_type=self.CONTENT_TYPES[format],
            data=data,
            size_bytes=len(data.encode('utf-8')) if isinstance(data, str) else len(data),
            generated_at=datetime.now()
        )

    def _to_geojson(self, data: Dict, geometry_type: str = "Point") -> str:
        """
        Convert data to GeoJSON format.

        Args:
            data: Data to convert
            geometry_type: Type of geometry (Point, Polygon, etc.)

        Returns:
            GeoJSON string
        """
        # Extract coordinates
        lat = data.get("latitude") or data.get("lat")
        lon = data.get("longitude") or data.get("lon")

        if not lat or not lon:
            # Try to get from nested structures
            imagery = data.get("imagery", {})
            lat = lat or imagery.get("latitude")
            lon = lon or imagery.get("longitude")

        if geometry_type == "Point" and lat and lon:
            geometry = {
                "type": "Point",
                "coordinates": [float(lon), float(lat)]
            }
        elif geometry_type == "Polygon" and "coordinates" in data:
            geometry = {
                "type": "Polygon",
                "coordinates": data["coordinates"]
            }
        else:
            # Default to null geometry
            geometry = None

        # Create properties (exclude coordinate fields)
        properties = {k: v for k, v in data.items()
                     if k not in ["latitude", "longitude", "lat", "lon", "coordinates", "geometry"]}

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

        return json.dumps(feature, indent=2, default=str)

    def _to_csv(self, data: List[Dict]) -> str:
        """
        Convert data to CSV format.

        Args:
            data: List of dictionaries to convert

        Returns:
            CSV string
        """
        if not data:
            return ""

        # Flatten nested dictionaries
        flat_data = []
        for item in data:
            flat_item = self._flatten_dict(item)
            flat_data.append(flat_item)

        # Get all unique keys
        fieldnames = set()
        for item in flat_data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))

        # Write to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flat_data)

        return output.getvalue()

    def _to_kml(self, data: Dict, name: str) -> str:
        """
        Convert data to KML format for Google Earth.

        Args:
            data: Data to convert
            name: Name for the KML placemark

        Returns:
            KML XML string
        """
        lat = data.get("latitude") or data.get("lat")
        lon = data.get("longitude") or data.get("lon")

        if not lat or not lon:
            # Try to get from nested structures
            imagery = data.get("imagery", {})
            lat = lat or imagery.get("latitude")
            lon = lon or imagery.get("longitude")

        # Create KML structure
        kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = SubElement(kml, 'Document')

        doc_name = SubElement(document, 'name')
        doc_name.text = "SAHOOL Satellite Analysis"

        placemark = SubElement(document, 'Placemark')
        placemark_name = SubElement(placemark, 'name')
        placemark_name.text = name

        # Add description with data
        description = SubElement(placemark, 'description')
        desc_text = self._format_kml_description(data)
        description.text = desc_text

        # Add point
        if lat and lon:
            point = SubElement(placemark, 'Point')
            coordinates = SubElement(point, 'coordinates')
            coordinates.text = f"{lon},{lat},0"

        # Convert to pretty XML string
        xml_string = tostring(kml, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")

    def _boundaries_to_kml(self, boundaries: List[Dict]) -> str:
        """
        Convert multiple boundaries to KML format.

        Args:
            boundaries: List of boundary data

        Returns:
            KML XML string
        """
        kml = Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        document = SubElement(kml, 'Document')

        doc_name = SubElement(document, 'name')
        doc_name.text = "SAHOOL Field Boundaries"

        for idx, boundary in enumerate(boundaries):
            placemark = SubElement(document, 'Placemark')
            placemark_name = SubElement(placemark, 'name')
            placemark_name.text = boundary.get("field_id", f"Field {idx + 1}")

            # Add description
            description = SubElement(placemark, 'description')
            description.text = self._format_kml_description(boundary)

            # Add polygon if coordinates exist
            coords = boundary.get("coordinates", [])
            if coords:
                polygon = SubElement(placemark, 'Polygon')
                outer = SubElement(polygon, 'outerBoundaryIs')
                linear_ring = SubElement(outer, 'LinearRing')
                coordinates = SubElement(linear_ring, 'coordinates')

                # Convert coordinates to KML format
                coord_text = []
                if isinstance(coords[0], list):
                    # It's a polygon
                    for coord in coords[0]:
                        if len(coord) >= 2:
                            coord_text.append(f"{coord[0]},{coord[1]},0")
                coordinates.text = " ".join(coord_text)

        # Convert to pretty XML string
        xml_string = tostring(kml, encoding='unicode')
        dom = minidom.parseString(xml_string)
        return dom.toprettyxml(indent="  ")

    def _format_kml_description(self, data: Dict) -> str:
        """
        Format data as HTML description for KML.

        Args:
            data: Data to format

        Returns:
            HTML string
        """
        lines = ["<![CDATA[<table>"]

        # Flatten and format data
        flat_data = self._flatten_dict(data)
        for key, value in flat_data.items():
            if value is not None:
                lines.append(f"<tr><td><b>{key}</b></td><td>{value}</td></tr>")

        lines.append("</table>]]>")
        return "".join(lines)

    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """
        Flatten nested dictionary.

        Args:
            d: Dictionary to flatten
            parent_key: Parent key for recursion
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k

            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to comma-separated strings
                if v and isinstance(v[0], dict):
                    # Skip nested list of dicts
                    items.append((new_key, f"[{len(v)} items]"))
                else:
                    items.append((new_key, ", ".join(str(x) for x in v)))
            else:
                items.append((new_key, v))

        return dict(items)

    def _flatten_analysis_for_csv(self, analysis: Dict) -> Dict:
        """
        Flatten analysis data specifically for CSV export.

        Args:
            analysis: Analysis data

        Returns:
            Flattened dictionary
        """
        flat = {
            "field_id": analysis.get("field_id"),
            "analysis_date": analysis.get("analysis_date"),
            "satellite": analysis.get("satellite"),
            "health_score": analysis.get("health_score"),
            "health_status": analysis.get("health_status"),
        }

        # Add indices
        indices = analysis.get("indices", {})
        for key, value in indices.items():
            flat[f"index_{key}"] = value

        # Add imagery info
        imagery = analysis.get("imagery", {})
        if imagery:
            flat["cloud_cover_percent"] = imagery.get("cloud_cover_percent")
            flat["acquisition_date"] = imagery.get("acquisition_date")
            flat["scene_id"] = imagery.get("scene_id")

        # Add anomalies
        anomalies = analysis.get("anomalies", [])
        flat["anomalies"] = ", ".join(anomalies) if anomalies else ""

        return flat

    def _flatten_prediction_for_csv(self, prediction: Dict) -> Dict:
        """
        Flatten yield prediction data for CSV export.

        Args:
            prediction: Prediction data

        Returns:
            Flattened dictionary
        """
        flat = {
            "field_id": prediction.get("field_id"),
            "prediction_date": prediction.get("prediction_date"),
            "crop_type": prediction.get("crop_type"),
            "predicted_yield_tons_ha": prediction.get("predicted_yield_tons_ha"),
            "confidence_score": prediction.get("confidence_score"),
            "quality_grade": prediction.get("quality_grade"),
        }

        # Add factors
        factors = prediction.get("factors", {})
        for key, value in factors.items():
            flat[f"factor_{key}"] = value

        # Add risks
        risks = prediction.get("risks", [])
        flat["risks"] = ", ".join(risks) if risks else ""

        return flat

    def generate_filename(
        self,
        prefix: str,
        field_id: str,
        format: ExportFormat
    ) -> str:
        """
        Generate filename with timestamp.

        Args:
            prefix: File prefix (e.g., "field_analysis")
            field_id: Field identifier
            format: Export format

        Returns:
            Filename string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = format.value

        # Sanitize field_id
        safe_field_id = "".join(c for c in field_id if c.isalnum() or c in "-_")

        return f"sahool_{prefix}_{safe_field_id}_{timestamp}.{extension}"
