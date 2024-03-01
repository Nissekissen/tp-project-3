package database

import (
	"fmt"
	"robotlager/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func Connect() {
	dsn := fmt.Sprintf(
		"host=localhost user=postgres password=postgres dbname=robotlager port=5432 sslmode=disable TimeZone=Europe/Stockholm")

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})

	if err != nil {
		panic("Could not connect to the database")
	}

	DB.Logger = logger.Default.LogMode(logger.Info)

	DB.AutoMigrate(&models.Item{})
	DB.AutoMigrate(&models.Cell{})
	DB.AutoMigrate(&models.QueueItem{})
}
