package database

import (
	"fmt"
	"os"
	"robotlager/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func Connect() {
	dsn := fmt.Sprintf(
		"host=db user=%s password=%s dbname=%s port=5432 sslmode=disable TimeZone=Europe/Stockholm",
		os.Getenv("DB_USER"),
		os.Getenv("DB_PASSWORD"),
		os.Getenv("DB_NAME"))

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
