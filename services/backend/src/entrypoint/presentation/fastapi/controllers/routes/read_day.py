from datetime import date

from fastapi import Response

from entrypoint.logic.services.read_day import read_day as service
from entrypoint.presentation.fastapi.controllers import cookies
from entrypoint.presentation.fastapi.controllers.parsers import valid_id_of
from entrypoint.presentation.fastapi.controllers.routers import router
from entrypoint.presentation.fastapi.controllers.tags import Tag
from entrypoint.presentation.fastapi.views.responses.bad.fault import (
    fault_response_model,
)
from entrypoint.presentation.fastapi.views.responses.bad.invalid_session_id_hex import (  # noqa: E501
    invalid_session_id_hex_response_model,
)
from entrypoint.presentation.fastapi.views.responses.bad.not_authenticated import (  # noqa: E501
    not_authenticated_response_model,
)
from entrypoint.presentation.fastapi.views.responses.common.model import (
    to_doc,
)
from entrypoint.presentation.fastapi.views.responses.common.record import (
    RecordSchema,
)
from entrypoint.presentation.fastapi.views.responses.ok.day.day import (
    DaySchema,
    day_response_model,
)


@router.get(
    "/user/day",
    tags=[Tag.current_user_endpoints],
    status_code=day_response_model.status_code,
    responses=to_doc(
        fault_response_model,
        not_authenticated_response_model,
        invalid_session_id_hex_response_model,
        day_response_model,
    ),
)
async def read_day(
    session_id_hex: cookies.session_id_cookie,
    date_: date,
) -> Response:
    session_id = valid_id_of(session_id_hex)

    if session_id is None:
        return invalid_session_id_hex_response_model.to_response()

    result = await service(session_id, date_)

    if result == "error":
        return fault_response_model.to_response()

    if result == "not_authenticated":
        return not_authenticated_response_model.to_response()

    if result.aqua_output is None:
        return fault_response_model.to_response()

    target = result.aqua_output.target_water_balance_milliliters
    body = DaySchema(
        user_id=result.aqua_output.user_id,
        target_water_balance_milliliters=target,
        date_=result.aqua_output.date_,
        water_balance_milliliters=result.aqua_output.water_balance_milliliters,
        result_code=result.aqua_output.result_code,
        real_result_code=result.aqua_output.real_result_code,
        is_result_pinned=result.aqua_output.is_result_pinned,
        records=tuple(map(RecordSchema.of, result.aqua_output.records)),
    )

    return day_response_model.to_response(body)
