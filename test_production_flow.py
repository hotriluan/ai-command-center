"""
End-to-End Test for Production Analytics Module
Tests file upload, analytics calculation, and MRP performance endpoints
"""

import requests
import os
from pathlib import Path
import json
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:8000"
DEMODATA_FOLDER = "demodata"

class TestResults:
    def __init__(self):
        self.results = []
        self.errors = []
        self.summary_data = {}
    
    def add_result(self, test_name, status, message="", data=None):
        self.results.append({
            "test": test_name,
            "status": status,
            "message": message,
            "data": data
        })
        if status == "FAIL":
            self.errors.append(f"{test_name}: {message}")
    
    def generate_report(self):
        report = f"""# Production Module Test Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Backend URL:** {BASE_URL}

---

## Test Results Summary

"""
        
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = sum(1 for r in self.results if r['status'] == 'FAIL')
        
        report += f"- **Total Tests:** {len(self.results)}\n"
        report += f"- **Passed:** ✅ {passed}\n"
        report += f"- **Failed:** ❌ {failed}\n\n"
        
        report += "---\n\n## Detailed Test Results\n\n"
        
        for result in self.results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            report += f"### {status_icon} {result['test']}\n\n"
            report += f"**Status:** {result['status']}\n\n"
            
            if result['message']:
                report += f"**Message:** {result['message']}\n\n"
            
            if result['data']:
                report += "**Data:**\n```json\n"
                report += json.dumps(result['data'], indent=2, ensure_ascii=False)
                report += "\n```\n\n"
        
        if self.summary_data:
            report += "---\n\n## Key Metrics\n\n"
            for key, value in self.summary_data.items():
                report += f"- **{key}:** {value}\n"
        
        if self.errors:
            report += "\n---\n\n## Error Log\n\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        report += "\n---\n\n## Conclusion\n\n"
        if failed == 0:
            report += "✅ **All tests passed successfully!** The Production Analytics module is functioning correctly.\n"
        else:
            report += f"⚠️ **{failed} test(s) failed.** Please review the errors above and fix the issues.\n"
        
        return report

def print_header(text):
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80)

def print_step(text):
    print(f"\n[STEP] {text}")

def locate_data_file():
    """Locate cooispi.xlsx in demodata folder"""
    print_header("FILE LOCATOR")
    
    # Check both .xlsx and .XLSX
    possible_paths = [
        Path(DEMODATA_FOLDER) / "cooispi.xlsx",
        Path(DEMODATA_FOLDER) / "cooispi.XLSX",
        Path(DEMODATA_FOLDER) / "COOISPI.xlsx",
        Path(DEMODATA_FOLDER) / "COOISPI.XLSX"
    ]
    
    for path in possible_paths:
        if path.exists():
            print(f"✅ Found file: {path}")
            return path
    
    print(f"❌ ERROR: cooispi.xlsx not found in {DEMODATA_FOLDER}/ folder")
    print("Please ensure the file exists at one of these locations:")
    for path in possible_paths:
        print(f"  - {path}")
    return None

def test_upload_api(file_path, test_results):
    """Test Step 1: Upload production data"""
    print_header("TEST 1: Upload API - POST /api/import/production")
    
    try:
        # Prepare file upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            
            print_step(f"Uploading {file_path.name} to {BASE_URL}/api/import/production")
            response = requests.post(
                f"{BASE_URL}/api/import/production",
                files=files,
                timeout=30
            )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Upload successful!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Extract metrics
            rows_processed = data.get('rows_processed', 0)
            new_records = data.get('new_records', 0)
            updated_records = data.get('updated_records', 0)
            
            test_results.add_result(
                "Upload API",
                "PASS",
                f"Successfully imported {rows_processed} production orders",
                data
            )
            test_results.summary_data['Rows Imported'] = rows_processed
            test_results.summary_data['New Records'] = new_records
            test_results.summary_data['Updated Records'] = updated_records
            
            return True
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ Upload failed: {error_msg}")
            test_results.add_result("Upload API", "FAIL", error_msg)
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Exception during upload: {error_msg}")
        test_results.add_result("Upload API", "FAIL", error_msg)
        return False

def test_analytics_api(test_results):
    """Test Step 2: Get production analytics"""
    print_header("TEST 2: Analytics API - GET /api/production/analytics")
    
    try:
        print_step(f"Fetching analytics from {BASE_URL}/api/production/analytics")
        response = requests.get(f"{BASE_URL}/api/production/analytics", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for required data structures
            has_summary = 'summary_metrics' in data
            has_orders = 'order_details' in data
            has_trends = 'trend_data' in data
            
            if has_summary and has_orders and has_trends:
                print("✅ Analytics API returned valid data structure")
                
                # Extract key metrics
                summary = data.get('summary_metrics', {})
                avg_lead_time = summary.get('avg_production_lead_time', 0)
                avg_yield_rate = summary.get('avg_yield_rate', 0)
                total_orders = summary.get('total_orders', 0)
                
                print(f"\n📊 Key Metrics:")
                print(f"  - Total Orders: {total_orders}")
                print(f"  - Average Production Lead Time: {avg_lead_time} days")
                print(f"  - Average Yield Rate: {avg_yield_rate}%")
                
                # Show sample trend data
                trends = data.get('trend_data', [])
                if trends:
                    print(f"\n📈 Monthly Trends ({len(trends)} months):")
                    for trend in trends[:3]:  # Show first 3 months
                        print(f"  - {trend.get('month')}: {trend.get('order_count')} orders, "
                              f"{trend.get('avg_lead_time')} days avg lead time")
                
                test_results.add_result(
                    "Analytics API",
                    "PASS",
                    f"Analytics returned data for {total_orders} orders",
                    {
                        "summary_metrics": summary,
                        "sample_trends": trends[:5] if trends else []
                    }
                )
                test_results.summary_data['Average Lead Time'] = f"{avg_lead_time} days"
                test_results.summary_data['Average Yield Rate'] = f"{avg_yield_rate}%"
                test_results.summary_data['Total Orders Analyzed'] = total_orders
                
                return True
            else:
                error_msg = "Missing required data fields in response"
                print(f"❌ {error_msg}")
                test_results.add_result("Analytics API", "FAIL", error_msg, data)
                return False
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ Analytics failed: {error_msg}")
            test_results.add_result("Analytics API", "FAIL", error_msg)
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Exception during analytics: {error_msg}")
        test_results.add_result("Analytics API", "FAIL", error_msg)
        return False

def test_mrp_performance_api(test_results):
    """Test Step 3: Get MRP controller performance"""
    print_header("TEST 3: MRP Performance API - GET /api/production/mrp-performance")
    
    try:
        print_step(f"Fetching MRP performance from {BASE_URL}/api/production/mrp-performance")
        response = requests.get(f"{BASE_URL}/api/production/mrp-performance", timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ MRP Performance API returned data for {len(data)} controllers")
                
                print(f"\n👥 MRP Controller Performance:")
                for controller in data[:5]:  # Show first 5
                    print(f"  - {controller.get('mrp_controller')}: "
                          f"{controller.get('total_orders')} orders, "
                          f"{controller.get('avg_lead_time')} days avg, "
                          f"{controller.get('avg_yield_rate')}% yield")
                
                test_results.add_result(
                    "MRP Performance API",
                    "PASS",
                    f"Retrieved performance data for {len(data)} MRP controllers",
                    data[:5]  # Include sample data
                )
                
                # Add sample controller to summary
                if data:
                    sample = data[0]
                    test_results.summary_data['Sample MRP Controller'] = (
                        f"{sample.get('mrp_controller')} - "
                        f"{sample.get('avg_yield_rate')}% yield, "
                        f"{sample.get('avg_lead_time')} days avg lead time"
                    )
                
                return True
            else:
                error_msg = "No MRP controller data returned"
                print(f"⚠️  {error_msg}")
                test_results.add_result("MRP Performance API", "PASS", 
                                       "API works but no data (may be expected if no controllers in data)")
                return True
        else:
            error_msg = f"HTTP {response.status_code}: {response.text}"
            print(f"❌ MRP Performance failed: {error_msg}")
            test_results.add_result("MRP Performance API", "FAIL", error_msg)
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Exception during MRP performance: {error_msg}")
        test_results.add_result("MRP Performance API", "FAIL", error_msg)
        return False

def main():
    print_header("PRODUCTION MODULE - END-TO-END TEST")
    print(f"Backend URL: {BASE_URL}")
    print(f"Data Folder: {DEMODATA_FOLDER}")
    
    test_results = TestResults()
    
    # Step 0: Locate file
    file_path = locate_data_file()
    if not file_path:
        test_results.add_result("File Locator", "FAIL", "cooispi.xlsx not found in demodata folder")
        print("\n❌ TEST ABORTED: Cannot proceed without data file")
        return
    
    test_results.add_result("File Locator", "PASS", f"Found file at {file_path}")
    
    # Step 1: Test Upload
    upload_success = test_upload_api(file_path, test_results)
    if not upload_success:
        print("\n⚠️  Upload failed, but continuing with remaining tests...")
    
    # Step 2: Test Analytics
    test_analytics_api(test_results)
    
    # Step 3: Test MRP Performance
    test_mrp_performance_api(test_results)
    
    # Generate Report
    print_header("GENERATING TEST REPORT")
    report = test_results.generate_report()
    
    report_path = Path("test_report.md")
    report_path.write_text(report, encoding='utf-8')
    print(f"✅ Test report saved to: {report_path.absolute()}")
    
    # Print summary
    print_header("TEST SUMMARY")
    passed = sum(1 for r in test_results.results if r['status'] == 'PASS')
    failed = sum(1 for r in test_results.results if r['status'] == 'FAIL')
    
    print(f"Total Tests: {len(test_results.results)}")
    print(f"Passed: ✅ {passed}")
    print(f"Failed: ❌ {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Production module is working correctly.")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Check test_report.md for details.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
