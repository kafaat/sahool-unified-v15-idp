#!/bin/bash

# SAHOOL Mobile App - Integration Tests Runner
# تشغيل اختبارات التكامل لتطبيق سهول

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEVICE_ID=${DEVICE_ID:-""}
SCREENSHOT_DIR="screenshots/integration"
REPORT_DIR="test_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/integration_test_report_$TIMESTAMP.html"

# Print with color
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════${NC}"
    echo ""
}

# Check if Flutter is installed
check_flutter() {
    print_header "Checking Flutter Installation"

    if ! command -v flutter &> /dev/null; then
        print_error "Flutter not found. Please install Flutter first."
        exit 1
    fi

    flutter --version
    print_success "Flutter is installed"
}

# Check for connected devices
check_devices() {
    print_header "Checking Connected Devices"

    flutter devices

    # Count number of connected devices
    DEVICE_COUNT=$(flutter devices | grep -c "•" || true)

    if [ "$DEVICE_COUNT" -eq 0 ]; then
        print_error "No devices connected. Please connect a device or start an emulator."
        exit 1
    fi

    print_success "$DEVICE_COUNT device(s) found"
}

# Start emulator if needed
start_emulator() {
    print_header "Starting Emulator (if needed)"

    # Check if an emulator is already running
    RUNNING_DEVICES=$(adb devices | grep -c "emulator" || true)

    if [ "$RUNNING_DEVICES" -eq 0 ]; then
        print_info "No emulator running. Starting default emulator..."

        # List available emulators
        EMULATORS=$(emulator -list-avds)

        if [ -z "$EMULATORS" ]; then
            print_warning "No emulators available. Please create one using Android Studio."
            return
        fi

        # Start first available emulator
        FIRST_EMULATOR=$(echo "$EMULATORS" | head -n 1)
        print_info "Starting emulator: $FIRST_EMULATOR"

        emulator -avd "$FIRST_EMULATOR" &

        # Wait for emulator to boot
        print_info "Waiting for emulator to boot..."
        adb wait-for-device

        # Wait additional time for full boot
        sleep 10

        print_success "Emulator started"
    else
        print_success "Emulator already running"
    fi
}

# Install dependencies
install_dependencies() {
    print_header "Installing Dependencies"

    print_info "Running flutter pub get..."
    flutter pub get

    print_success "Dependencies installed"
}

# Create directories
create_directories() {
    print_header "Creating Output Directories"

    mkdir -p "$SCREENSHOT_DIR"
    mkdir -p "$REPORT_DIR"

    print_success "Directories created"
}

# Run all integration tests
run_all_tests() {
    print_header "Running All Integration Tests"

    TEST_FILES=(
        "integration_test/app_test.dart"
        "integration_test/features/auth_test.dart"
        "integration_test/features/fields_test.dart"
        "integration_test/features/satellite_test.dart"
        "integration_test/features/vra_test.dart"
        "integration_test/features/inventory_test.dart"
    )

    FAILED_TESTS=()
    PASSED_TESTS=()

    for TEST_FILE in "${TEST_FILES[@]}"; do
        print_info "Running: $TEST_FILE"

        if [ -n "$DEVICE_ID" ]; then
            DEVICE_ARG="-d $DEVICE_ID"
        else
            DEVICE_ARG=""
        fi

        # Run test and capture output
        if flutter test $DEVICE_ARG "$TEST_FILE"; then
            print_success "PASSED: $TEST_FILE"
            PASSED_TESTS+=("$TEST_FILE")
        else
            print_error "FAILED: $TEST_FILE"
            FAILED_TESTS+=("$TEST_FILE")
        fi

        echo ""
    done

    # Print summary
    print_header "Test Summary"

    echo "Total Tests: ${#TEST_FILES[@]}"
    echo -e "${GREEN}Passed: ${#PASSED_TESTS[@]}${NC}"
    echo -e "${RED}Failed: ${#FAILED_TESTS[@]}${NC}"

    if [ ${#FAILED_TESTS[@]} -gt 0 ]; then
        echo ""
        print_error "Failed Tests:"
        for FAILED in "${FAILED_TESTS[@]}"; do
            echo "  - $FAILED"
        done
        return 1
    else
        print_success "All tests passed!"
        return 0
    fi
}

# Run specific test file
run_test() {
    local TEST_FILE=$1

    print_header "Running Test: $TEST_FILE"

    if [ ! -f "$TEST_FILE" ]; then
        print_error "Test file not found: $TEST_FILE"
        exit 1
    fi

    if [ -n "$DEVICE_ID" ]; then
        DEVICE_ARG="-d $DEVICE_ID"
    else
        DEVICE_ARG=""
    fi

    flutter test $DEVICE_ARG "$TEST_FILE"
}

# Generate HTML report
generate_report() {
    print_header "Generating Test Report"

    # This is a basic report. In production, use proper test reporting tools
    cat > "$REPORT_FILE" <<EOF
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAHOOL Integration Test Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2E7D32;
            border-bottom: 3px solid #2E7D32;
            padding-bottom: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h2 {
            margin: 0;
            font-size: 48px;
        }
        .stat-card p {
            margin: 10px 0 0 0;
            color: #666;
        }
        .passed {
            background: #E8F5E9;
            border: 2px solid #4CAF50;
        }
        .failed {
            background: #FFEBEE;
            border: 2px solid #F44336;
        }
        .total {
            background: #E3F2FD;
            border: 2px solid #2196F3;
        }
        .timestamp {
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>تقرير اختبارات التكامل - SAHOOL</h1>
        <div class="timestamp">تاريخ التشغيل: $TIMESTAMP</div>

        <div class="summary">
            <div class="stat-card total">
                <h2>6</h2>
                <p>إجمالي الاختبارات</p>
            </div>
            <div class="stat-card passed">
                <h2 id="passed-count">-</h2>
                <p>نجح</p>
            </div>
            <div class="stat-card failed">
                <h2 id="failed-count">-</h2>
                <p>فشل</p>
            </div>
        </div>

        <h2>ملفات الاختبار</h2>
        <ul>
            <li>app_test.dart - الاختبارات الرئيسية</li>
            <li>features/auth_test.dart - اختبارات المصادقة</li>
            <li>features/fields_test.dart - اختبارات إدارة الحقول</li>
            <li>features/satellite_test.dart - اختبارات صور الأقمار</li>
            <li>features/vra_test.dart - اختبارات الزراعة الدقيقة</li>
            <li>features/inventory_test.dart - اختبارات إدارة المخزون</li>
        </ul>

        <h2>لقطات الشاشة</h2>
        <p>موقع اللقطات: $SCREENSHOT_DIR</p>
    </div>
</body>
</html>
EOF

    print_success "Report generated: $REPORT_FILE"
}

# Upload screenshots (placeholder)
upload_screenshots() {
    print_header "Processing Screenshots"

    SCREENSHOT_COUNT=$(find "$SCREENSHOT_DIR" -type f 2>/dev/null | wc -l)

    print_info "Found $SCREENSHOT_COUNT screenshots in $SCREENSHOT_DIR"

    # In production, upload to cloud storage (S3, Firebase, etc.)
    # aws s3 sync $SCREENSHOT_DIR s3://your-bucket/screenshots/

    print_success "Screenshots processed"
}

# Clean up
cleanup() {
    print_header "Cleaning Up"

    # Kill emulator if we started it
    # pkill -f "emulator"

    print_success "Cleanup complete"
}

# Main menu
show_help() {
    echo "SAHOOL Integration Tests Runner"
    echo ""
    echo "Usage: ./run_tests.sh [option] [test_file]"
    echo ""
    echo "Options:"
    echo "  -a, --all              Run all integration tests"
    echo "  -t, --test <file>      Run specific test file"
    echo "  -d, --device <id>      Specify device ID"
    echo "  -e, --emulator         Start emulator before testing"
    echo "  -r, --report           Generate HTML report after tests"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_tests.sh --all"
    echo "  ./run_tests.sh --test integration_test/features/auth_test.dart"
    echo "  ./run_tests.sh --all --device emulator-5554"
    echo "  ./run_tests.sh --all --emulator --report"
}

# Parse command line arguments
SHOULD_START_EMULATOR=false
SHOULD_GENERATE_REPORT=false
RUN_ALL=false
TEST_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        -t|--test)
            TEST_FILE="$2"
            shift 2
            ;;
        -d|--device)
            DEVICE_ID="$2"
            shift 2
            ;;
        -e|--emulator)
            SHOULD_START_EMULATOR=true
            shift
            ;;
        -r|--report)
            SHOULD_GENERATE_REPORT=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
main() {
    print_header "SAHOOL Integration Tests - اختبارات التكامل"

    check_flutter
    install_dependencies
    create_directories

    if [ "$SHOULD_START_EMULATOR" = true ]; then
        start_emulator
    fi

    check_devices

    # Run tests
    if [ "$RUN_ALL" = true ]; then
        run_all_tests
        TEST_RESULT=$?
    elif [ -n "$TEST_FILE" ]; then
        run_test "$TEST_FILE"
        TEST_RESULT=$?
    else
        print_error "No test specified. Use --all or --test <file>"
        show_help
        exit 1
    fi

    # Generate report if requested
    if [ "$SHOULD_GENERATE_REPORT" = true ]; then
        generate_report
        upload_screenshots
    fi

    # Exit with test result
    if [ $TEST_RESULT -eq 0 ]; then
        print_header "All Tests Passed! ✓"
        exit 0
    else
        print_header "Some Tests Failed ✗"
        exit 1
    fi
}

# Run main function
main
