from typing import Dict
from pydantic import BaseModel
from database.AuthDB import get_db_connection


class MonitorCreate(BaseModel):
    monitorid: int
    userid: int
    sitename: str
    site_url: str
    monitor_created: str
    interval: int

def _create_new_monitor(monitor: Dict[str, any]):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO monitors (monitorid,userid, sitename, site_url)
            VALUES (%s, %s, %s, %s) RETURNING monitorid
                       """, (monitor["monitorid"], monitor["userid"], monitor["sitename"], monitor["site_url"]))

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


def get_monitor_info(monitor_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM monitors WHERE monitorid = %s", (str(monitor_id),))
        monitor = cursor.fetchone()
        monitor = {
            "monitorid": monitor[0],
            "userid": monitor[1],
            "sitename": monitor[2],
            "site_url": monitor[3],
            "monitor_created": monitor[4],
            "is_active": monitor[5]
        }
        # print(monitor)
        if monitor:
            return {"success": True, "data": monitor}
        else:
            return {"success": False, "message": "Monitor not found"}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()





def get_monitor_by_user(user_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM monitors WHERE userid = %s", (user_id,))
        monitors = cursor.fetchall()
        if monitors:
            monitors = [
                {
                    "monitorid": monitor[0],
                    "userid": monitor[1],
                    "sitename": monitor[2],
                    "site_url": monitor[3],
                    "monitor_created": monitor[4],
                    "is_active": monitor[5]
                }
                for monitor in monitors
            ]
            return {"success": True, "data": monitors}
        else:
            return {"success": False, "message": "No monitors found for user"}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()
