package models

type QueueStatus int

const (
	QUEUED QueueStatus = iota
	IN_PROGRESS
	COMPLETED
	FAILED
)

type QueueItemType int

const (
	ORDER QueueItemType = iota
	RESTOCK
	CREATED
	DELETED
)

type Cell struct {
	ID uint `json:"id" gorm:"primaryKey;unique;not null"`
	X  uint `json:"x" gorm:"not null"`
	Y  uint `json:"y" gorm:"not null"`
	Z  uint `json:"z" gorm:"not null"`
}

type Item struct {
	ID     uint   `json:"id" gorm:"primaryKey;unique;not null"`
	Name   string `json:"name" gorm:"not null"`
	Amount uint   `json:"amount" gorm:"not null"`
	CellID uint   `json:"cell_id"`
}

type QueueItem struct {
	ID     uint `json:"id" gorm:"primaryKey;unique;not null"`
	ItemID uint `json:"item_id" gorm:"not null"`
	Amount int  `json:"amount" gorm:"not null"`
	Status int  `json:"status" gorm:"not null"`
	Type   int  `json:"type" gorm:"not null"`
}

// Since the `instructions` table is not used in the application, it is not included in the models.