package models

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
	CellID uint   `json:"cell_id" gorm:"not null"`
}

type QueueItem struct {
	ID       uint   `json:"id" gorm:"primaryKey;unique;not null"`
	FromID   uint   `json:"from_id"`
	ToID     uint   `json:"to_id"`
	ItemID   uint   `json:"item_id" gorm:"not null"`
	Amount   int    `json:"amount" gorm:"not null"`
	Status   string `json:"status" gorm:"not null"`
	Position uint   `json:"position" gorm:"not null"`
	Type     string `json:"type" gorm:"not null"`
}
