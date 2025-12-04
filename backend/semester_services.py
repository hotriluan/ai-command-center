"""
Semester-aware performance functions
"""
from sqlalchemy.orm import Session
from sqlalchemy import text

def get_performance_by_semester(db: Session, year: int):
    """
    Get sales performance grouped by semester
    Returns data for Semester 1 and Semester 2 separately
    """
    try:
        query = text("""
            SELECT 
                salesman_name,
                semester,
                SUM(total_revenue) as revenue,
                SUM(total_profit) as profit,
                MAX(total_target) as target,
                AVG(achievement_percentage) as achievement
            FROM view_sales_performance_v2
            WHERE year = :year
            GROUP BY salesman_name, semester
            ORDER BY salesman_name, semester
        """)
        
        result = db.execute(query, {"year": year}).fetchall()
        
        # Group by salesman
        performance_data = {}
        for row in result:
            salesman = row[0]
            semester = row[1]
            
            if salesman not in performance_data:
                performance_data[salesman] = {
                    "name": salesman,
                    "semester_1": {"revenue": 0, "profit": 0, "target": 0, "achievement": 0},
                    "semester_2": {"revenue": 0, "profit": 0, "target": 0, "achievement": 0}
                }
            
            sem_key = f"semester_{semester}"
            performance_data[salesman][sem_key] = {
                "revenue": float(row[2] or 0),
                "profit": float(row[3] or 0),
                "target": float(row[4] or 0),
                "achievement": float(row[5] or 0)
            }
        
        return list(performance_data.values())
        
    except Exception as e:
        print(f"Error in get_performance_by_semester: {e}")
        import traceback
        traceback.print_exc()
        return []
