package handlers

import (
	"robotlager/database"
	"robotlager/models"

	"github.com/gofiber/fiber/v2"
)

func GetQueue(c *fiber.Ctx) error {
	// Get all queue items from the database

	queueItems := []models.QueueItem{}

	query := database.DB.Model(&models.QueueItem{})
	query.Find(&queueItems)
	if query.Error != nil {
		return c.Status(500).SendString("Could not get queue items")
	}

	return c.JSON(queueItems)
}

func AddItemToQueue(c *fiber.Ctx) error {

	type QueueItemInput struct {
		ItemID uint `json:"item_id"`
		Amount uint `json:"amount"`
		ToID   uint `json:"to_id"`
	}

	var input QueueItemInput
	if err := c.BodyParser(&input); err != nil {
		return c.Status(400).SendString("Could not parse JSON")
	}

	// Get current queue length
	var queueLength int64
	query := database.DB.Model(&models.QueueItem{}).Count(&queueLength)

	if query.Error != nil {
		return c.Status(500).SendString("Could not get queue length")
	}

	// Create new queue item
	queueItem := models.QueueItem{
		ItemID:   input.ItemID,
		Amount:   input.Amount,
		ToID:     input.ToID,
		Status:   "queued",
		Position: uint(queueLength + 1),
	}
	database.DB.Create(&queueItem)

	return c.Status(fiber.StatusCreated).JSON(queueItem)
}
