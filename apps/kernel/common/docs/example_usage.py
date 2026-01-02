"""
Example usage of SAHOOL API Documentation Generator
مثال على استخدام مولد توثيق واجهة برمجة تطبيقات سحول
"""

from pathlib import Path
from api_docs_generator import APIDocsGenerator, APICategory


def example_basic_usage():
    """
    Basic usage example - Generate all documentation
    مثال الاستخدام الأساسي - إنشاء جميع الوثائق
    """
    print("Example 1: Basic Usage")
    print("=" * 60)

    # Initialize generator with default paths
    generator = APIDocsGenerator()

    # Scan all services
    generator.scan_all_services()

    # Generate all documentation
    generator.generate_openapi_spec()
    generator.generate_markdown_docs()
    generator.generate_postman_collection()

    print(f"\n✅ Generated docs for {len(generator.services)} services")


def example_custom_paths():
    """
    Example with custom paths
    مثال مع مسارات مخصصة
    """
    print("\nExample 2: Custom Paths")
    print("=" * 60)

    # Custom directories
    generator = APIDocsGenerator(
        services_dir="/custom/path/to/services",
        output_dir="/custom/path/to/output"
    )

    # Scan and generate
    generator.scan_all_services()
    generator.generate_openapi_spec("custom_openapi.json")
    generator.generate_postman_collection("custom.postman_collection.json")


def example_single_service():
    """
    Scan and document a single service
    فحص وتوثيق خدمة واحدة
    """
    print("\nExample 3: Single Service")
    print("=" * 60)

    generator = APIDocsGenerator()

    # Scan a specific service
    service = generator._scan_service(
        "weather-core",
        Path("apps/services/weather-core/src/main.py")
    )

    if service:
        print(f"Service: {service.title}")
        print(f"Description: {service.description}")
        print(f"Port: {service.port}")
        print(f"Endpoints: {len(service.endpoints)}")
        print("\nEndpoints:")
        for endpoint in service.endpoints:
            print(f"  {endpoint.method:6} {endpoint.path}")
            print(f"         {endpoint.summary}")


def example_category_analysis():
    """
    Analyze endpoints by category
    تحليل نقاط النهاية حسب الفئة
    """
    print("\nExample 4: Category Analysis")
    print("=" * 60)

    generator = APIDocsGenerator()
    generator.scan_all_services()

    print(f"\nEndpoints by Category:")
    print(f"{'-' * 60}")

    for category in APICategory:
        endpoints = generator.endpoints_by_category[category]
        if endpoints:
            print(f"{category.value:20} {len(endpoints):3} endpoints")

            # Show first 3 endpoints
            for endpoint in endpoints[:3]:
                print(f"  - {endpoint.method:6} {endpoint.path}")


def example_export_service_list():
    """
    Export list of all services with metadata
    تصدير قائمة بجميع الخدمات مع البيانات الوصفية
    """
    print("\nExample 5: Service List Export")
    print("=" * 60)

    generator = APIDocsGenerator()
    generator.scan_all_services()

    # Create service list
    services_list = []
    for name, service in sorted(generator.services.items()):
        services_list.append({
            "name": name,
            "title": service.title,
            "description": service.description,
            "description_ar": service.description_ar,
            "port": service.port,
            "endpoint_count": len(service.endpoints),
            "version": service.version
        })

    # Print as table
    print(f"\n{'Service':<30} {'Port':<6} {'Endpoints':<10} {'Version':<10}")
    print("-" * 60)
    for svc in services_list:
        print(f"{svc['name']:<30} {svc['port']:<6} {svc['endpoint_count']:<10} {svc['version']:<10}")


def example_search_endpoints():
    """
    Search for specific endpoints
    البحث عن نقاط نهاية محددة
    """
    print("\nExample 6: Search Endpoints")
    print("=" * 60)

    generator = APIDocsGenerator()
    generator.scan_all_services()

    # Search for endpoints containing 'profitability'
    search_term = "profitability"
    matching_endpoints = []

    for service in generator.services.values():
        for endpoint in service.endpoints:
            if search_term in endpoint.path.lower() or search_term in endpoint.summary.lower():
                matching_endpoints.append({
                    "service": service.name,
                    "method": endpoint.method,
                    "path": endpoint.path,
                    "summary": endpoint.summary
                })

    print(f"\nFound {len(matching_endpoints)} endpoints matching '{search_term}':")
    print("-" * 60)
    for ep in matching_endpoints:
        print(f"{ep['method']:6} {ep['path']}")
        print(f"       Service: {ep['service']}")
        print(f"       {ep['summary']}")
        print()


def example_generate_statistics():
    """
    Generate statistics about the API
    إنشاء إحصائيات حول API
    """
    print("\nExample 7: API Statistics")
    print("=" * 60)

    generator = APIDocsGenerator()
    generator.scan_all_services()

    # Calculate statistics
    total_services = len(generator.services)
    total_endpoints = sum(len(s.endpoints) for s in generator.services.values())

    # Count by HTTP method
    methods = {}
    for service in generator.services.values():
        for endpoint in service.endpoints:
            methods[endpoint.method] = methods.get(endpoint.method, 0) + 1

    # Count services by port range
    port_ranges = {
        "8000-8009": 0,
        "8010-8019": 0,
        "8020-8099": 0,
        "8100-8199": 0,
        "Other": 0
    }

    for service in generator.services.values():
        port = service.port
        if 8000 <= port <= 8009:
            port_ranges["8000-8009"] += 1
        elif 8010 <= port <= 8019:
            port_ranges["8010-8019"] += 1
        elif 8020 <= port <= 8099:
            port_ranges["8020-8099"] += 1
        elif 8100 <= port <= 8199:
            port_ranges["8100-8199"] += 1
        else:
            port_ranges["Other"] += 1

    # Print statistics
    print(f"\n📊 API Statistics:")
    print(f"{'=' * 60}")
    print(f"Total Services:        {total_services}")
    print(f"Total Endpoints:       {total_endpoints}")
    print(f"Avg Endpoints/Service: {total_endpoints / total_services:.1f}")
    print()

    print(f"Endpoints by Method:")
    for method, count in sorted(methods.items()):
        print(f"  {method:6} {count:3}")
    print()

    print(f"Services by Port Range:")
    for port_range, count in port_ranges.items():
        if count > 0:
            print(f"  {port_range:12} {count:3}")


def main():
    """Run all examples"""
    examples = [
        example_basic_usage,
        example_single_service,
        example_category_analysis,
        example_export_service_list,
        example_search_endpoints,
        example_generate_statistics,
    ]

    print("=" * 60)
    print("SAHOOL API Documentation Generator - Examples")
    print("مولد توثيق واجهة برمجة تطبيقات سحول - أمثلة")
    print("=" * 60)

    for i, example in enumerate(examples, 1):
        try:
            example()
        except Exception as e:
            print(f"\n⚠️  Example {i} failed: {e}")

    print("\n" + "=" * 60)
    print("✅ All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
