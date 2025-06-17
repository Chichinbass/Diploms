from db.models import Route
from db.db_session import get_session
from sqlalchemy import select, delete


async def save_route(telegram_id: int, city_from: str, city_to: str, route_name: str = None):
    async for session in get_session():
        route = Route(
            telegram_id=telegram_id,
            city_from=city_from,
            city_to=city_to,
            route_name=route_name
        )
        session.add(route)
        await session.commit()
async def get_routes_by_user(telegram_id: int):
    async for session in get_session():
        stmt = select(Route).where(Route.telegram_id == telegram_id)
        result = await session.execute(stmt)
        routes = result.scalars().all()
        return routes

async def delete_route(route_id: int):
    async for session in get_session():
        stmt = delete(Route).where(Route.id == route_id)
        await session.execute(stmt)
        await session.commit()