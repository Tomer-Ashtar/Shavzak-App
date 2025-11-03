from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..db import get_db
from .. import models, schemas


router = APIRouter(prefix="/api/workers", tags=["workers"])


@router.get("", response_model=List[schemas.WorkerRead])
def list_workers(db: Session = Depends(get_db)):
    return db.query(models.Worker).order_by(models.Worker.id.asc()).all()


@router.post("", response_model=schemas.WorkerRead, status_code=status.HTTP_201_CREATED)
def create_worker(payload: schemas.WorkerCreate, db: Session = Depends(get_db)):
    worker = models.Worker(
        name=payload.name,
        title=payload.title,
        hard_chores_counter=payload.hard_chores_counter,
        outer_partner_counter=payload.outer_partner_counter,
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.get("/{worker_id}", response_model=schemas.WorkerRead)
def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="worker_not_found")
    return worker


@router.put("/{worker_id}", response_model=schemas.WorkerRead)
def update_worker(worker_id: int, payload: schemas.WorkerUpdate, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="worker_not_found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(worker, field, value)
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(models.Worker).get(worker_id)
    if not worker:
        raise HTTPException(status_code=404, detail="worker_not_found")
    db.delete(worker)
    db.commit()
    return None

