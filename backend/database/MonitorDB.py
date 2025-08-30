from pydantic import BaseModel
from database.AuthDB import get_db_connection


class MonitorCreate(BaseModel):
    monitorid: int
    userid: int
    sitename: str
    site_url: str
    monitor_created: str
    interval: int

def _create_new_monitor(monitor: MonitorCreate):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        print("hiiii")
        cursor.execute("""INSERT INTO monitors (monitorid,userid, sitename, site_url, monitor_created)
            VALUES (%s, %s, %s, %s, %s) RETURNING monitorid
                       """, (monitor.monitorid, monitor.userid, monitor.sitename, monitor.site_url, monitor.monitor_created))

        result = cursor.fetchone()
        if result:
            monitor_id = result[0]
            connection.commit()
            return {"success": True, "message": "Monitor created successfully", "monitor_id": monitor_id}
        else:
            return {"success": False, "message": "Failed to create monitor"}
            
    except Exception as e:
        connection.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()


def _delete_monitor(monitor_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM monitors WHERE monitorid = %s", (monitor_id,))
        if cursor.rowcount > 0:
            connection.commit()
            return {"success": True, "message": "Monitor deleted successfully"}
        else:
            return {"success": False, "message": "Monitor not found"}
    except Exception as e:
        connection.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()

# if __name__ == "__main__":
#     data= {
#         "monitorid": 101,
#         "userid": 4,
#         "sitename": "Example Site",
#         "site_url": "https://www.example.com",
#         "monitor_created": "2023-10-01"
#     }
#     result = _delete_monitor(101)
#     print(result)





