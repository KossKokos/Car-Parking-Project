import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from car_parking.src.routes import auth, users, parking, admin
from car_parking.src.database.db import get_db
from car_parking.src.repository import tariff as repository_tariff, parking as repository_parking

app = FastAPI(debug=True)

# # create route so i don't need to add contacts/... everytime to my routes functions
app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(parking.router, prefix='/api')
app.include_router(admin.router, prefix='/api')



@app.get("/")
async def read_root():

    return {"message": "Hello World!"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):

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


async def main():
    # Establish database connection
    db = next(get_db())
    # Seed tariff table if empty
    await repository_tariff.seed_tariff_table(db)
    await repository_parking.seed_parking_count(db)
    # Close database connection
    db.close()
    # Start FastAPI server
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())

