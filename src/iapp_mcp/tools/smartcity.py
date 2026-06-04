"""Smart city and data tools: license plate, meter OCR, route optimization, Thai holidays."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from ..app import mcp
from ..client import IAppAPIError, format_json_response, request

_READONLY = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}


@mcp.tool(
    name="iapp_license_plate_ocr",
    annotations={"title": "Thai License Plate Recognition", **_READONLY},
)
async def iapp_license_plate_ocr(file_path: str) -> str:
    """Read a Thai vehicle license plate from an image, including vehicle attributes.

    Args:
        file_path: Local path to the vehicle image (JPEG/PNG, max 2MB).

    Returns:
        JSON string with plate number, province, vehicle brand/model/color/body type,
        orientation and confidence. Cost: 0.75 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/smart-city/license-plate-ocr",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_meter_ocr",
    annotations={"title": "Power/Water Meter OCR", **_READONLY},
)
async def iapp_meter_ocr(file_path: str) -> str:
    """Read the digits from a power meter or water meter photo.

    Args:
        file_path: Local path to the meter photo (JPEG/PNG).

    Returns:
        JSON string with the meter reading (label field). Cost: 1 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/smart-city/power-meter-and-water-meter/file",
            file_fields=[("file", file_path)],
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


class RouteStop(BaseModel):
    """A delivery stop for route optimization."""

    customerName: str = Field(description="Customer name")
    customerPhone: str = Field(description="Customer phone number")
    customerAddress: str = Field(description="Delivery address")
    item: str = Field(description="Item to deliver")
    customerMail: Optional[str] = Field(default=None, description="Customer email")
    instructionCC: Optional[str] = Field(default=None, description="Instructions for call center")
    instructionDriver: Optional[str] = Field(default=None, description="Instructions for driver")
    latitude: Optional[float] = Field(default=None, description="Stop latitude")
    longitude: Optional[float] = Field(default=None, description="Stop longitude")


@mcp.tool(
    name="iapp_route_optimization",
    annotations={"title": "Automatic Route Optimization", **_READONLY},
)
async def iapp_route_optimization(
    origin_address: str,
    origin_latitude: float,
    origin_longitude: float,
    stops: List[RouteStop],
    driver_count: int = -1,
) -> str:
    """Optimize delivery routes for one or more drivers from an origin to up to 100 stops.

    Args:
        origin_address: Starting point address.
        origin_latitude: Starting point latitude.
        origin_longitude: Starting point longitude.
        stops: Delivery stops (max 100). Addresses are geocoded automatically if
            latitude/longitude are omitted.
        driver_count: Number of drivers, or -1 to auto-optimize.

    Returns:
        JSON string with optimized job assignments, route order, number of drops and
        total distance in km. Cost: 1 IC.
    """
    try:
        response = await request(
            "POST",
            "/v3/store/smart-city/automatic-route-optimization",
            json_body={
                "driverSize": driver_count,
                "origin": {
                    "address": origin_address,
                    "latitude": origin_latitude,
                    "longitude": origin_longitude,
                },
                "routes": [
                    stop.model_dump(exclude_none=True) for stop in stops
                ],
            },
        )
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)


@mcp.tool(
    name="iapp_thai_holidays",
    annotations={"title": "Thai Holiday Data", **_READONLY},
)
async def iapp_thai_holidays(
    year: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days_before: int = 0,
    days_after: int = 365,
    holiday_type: Literal["public", "financial", "both"] = "public",
) -> str:
    """Get Thai public and financial holidays.

    Three query modes (in priority order):
        1. year: all holidays in a calendar year (2020-2030)
        2. start_date + end_date: holidays in a date range (YYYY-MM-DD)
        3. days_before/days_after: holidays relative to today (default: next 365 days)

    Args:
        year: Calendar year (2020-2030).
        start_date: Range start date (YYYY-MM-DD), requires end_date.
        end_date: Range end date (YYYY-MM-DD), requires start_date.
        days_before: Days before today to include (max 1825).
        days_after: Days after today to include (max 1825).
        holiday_type: 'public', 'financial' (bank holidays), or 'both'.

    Returns:
        JSON string with holiday dates, Thai names, weekdays and types. Cost: 0.1 IC.
    """
    try:
        params = {"holiday_type": holiday_type}
        if year is not None:
            response = await request(
                "GET", f"/v3/store/data/thai-holiday/year/{year}", params=params
            )
        elif start_date and end_date:
            params.update({"start_date": start_date, "end_date": end_date})
            response = await request("GET", "/v3/store/data/thai-holiday/range", params=params)
        else:
            params.update({"days_before": days_before, "days_after": days_after})
            response = await request("GET", "/v3/store/data/thai-holiday", params=params)
        return format_json_response(response)
    except IAppAPIError as e:
        return str(e)
