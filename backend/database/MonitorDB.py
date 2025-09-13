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
        print("before insert:", monitor)
        cursor.execute(
            """INSERT INTO monitors (monitorid, userid, sitename, site_url, monitor_created)
               VALUES (%s, %s, %s, %s, %s) RETURNING monitorid""",
            (monitor["monitorid"], monitor["userid"], monitor["sitename"], monitor["site_url"],
             monitor["monitor_created"])
        )

        result = cursor.fetchone()
        print("after insert:", result)
        if result:
            monitor_id = result[0]
            connection.commit()
            print("after commit:", monitor_id)
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
        if not monitor:
            return {"success": False, "message": "Monitor not found"}
        monitor = {
            "monitorid": monitor[0],
            "userid": monitor[1],
            "sitename": monitor[2],
            "site_url": monitor[3],
            "monitor_created": monitor[4],
            "interval": monitor[5],
            "is_active": monitor[6]
        }
        return {"success": True, "data": monitor}
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
        if not monitors:
            return {"success": False, "message": "No monitors found for user"}
        monitors = [
            {
                "monitorid": monitor[0],
                "userid": monitor[1],
                "sitename": monitor[2],
                "site_url": monitor[3],
                "monitor_created": monitor[4],
                "interval": monitor[5],
                "is_active": monitor[6]
            }
            for monitor in monitors
        ]
        return {"success": True, "data": monitors}
    except Exception as e:
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()

def _edit_monitor(monitor_id: int, update_data: Dict[str, any]):
    """Update monitor fields in the database, safely mapping API fields to DB columns."""
    if not update_data:
        return {"success": False, "message": "No data provided to update"}

    # Map API field names to DB columns
    field_map = {
        "friendlyName": "sitename",
        "site_url": "site_url",
        # "interval": None,  # interval not in DB, skip it
        "is_active": "is_active",
        "status": "status",
    }

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        set_clauses = []
        values = []

        for key, value in update_data.items():
            db_key = field_map.get(key)
            if not db_key:
                # Skip fields that do not exist in DB
                continue
            set_clauses.append(f"{db_key} = %s")
            values.append(value)

        if not set_clauses:
            return {"success": False, "message": "No valid fields to update"}

        values.append(monitor_id)
        set_clause_str = ", ".join(set_clauses)

        cursor.execute(f"UPDATE monitors SET {set_clause_str} WHERE monitorid = %s", tuple(values))
        if cursor.rowcount > 0:
            connection.commit()
            return {"success": True, "message": "Monitor updated successfully"}
        else:
            return {"success": False, "message": "Monitor not found"}
    except Exception as e:
        connection.rollback()
        return {"success": False, "message": f"Database error: {str(e)}"}
    finally:
        cursor.close()
        connection.close()
