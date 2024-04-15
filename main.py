import uvicorn
import asyncio
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from car_parking.src.routes import auth, users, parking, admin
from car_parking.src.database.db import get_db
from car_parking.src.repository import tariff as repository_tariff, parking as repository_parking
import schedule

app = FastAPI(debug=True)

# # create route so i don't need to add contacts/... everytime to my routes functions
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(parking.router, prefix='/api')
app.include_router(admin.router, prefix='/api')
# app.include_router(rating.router, prefix='/api')
# app.include_router(comments.router, prefix='/api')


@app.get("/")
async def read_root():
    """
    The read_root function returns a JSON object with the message: Hello World.
    
    :return: A dict
    """
    return {"message": "Hello World!"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    The healthchecker function is used to check the health of the database.
    It will return a 200 status code if it can successfully connect to the database,
    and a 500 status code otherwise.
    
    :param db: Session: Pass the database connection to the function
    :return: A dict with a message
    :doc-author: Trelent
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        print(result)
        if result is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Error connecting to the database")


async def schedule_check_parking(db: Session):
    schedule.every().day.at("00:00").do(await repository_parking.check_parking_max_limit, db)

    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Sleep for 1 second to avoid high CPU usage

async def main():

    db = next(get_db())
    await repository_tariff.seed_tariff_table(db)
    await repository_parking.seed_parking_count(db)
    db.close()
    
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)

    asyncio.create_task(schedule_check_parking(db))

if __name__ == '__main__':
    asyncio.run(main())
