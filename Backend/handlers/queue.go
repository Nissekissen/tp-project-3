package handlers

import (
	"fmt"
	"robotlager/database"
	"robotlager/models"

	"github.com/gofiber/fiber/v2"
)

func GetQueue(c *fiber.Ctx) error {
	// Get all queue items from the database

	itemId := c.Query("item_id")

	queueItems := []models.QueueItem{}

	query := database.DB.Model(&models.QueueItem{})
	if itemId != "" {
		query.Where("item_id = ?", itemId)
	}

	query.Find(&queueItems)
	if query.Error != nil {
		return c.Status(500).SendString("Could not get queue items")
	}

	return c.JSON(queueItems)
}

func AddItemToQueue(c *fiber.Ctx) error {

	// To simplify for frontend, user will only input itemID and amount
	type QueueItemInput struct {
		ItemID uint `json:"item_id"`
		Amount int  `json:"amount"`
	}

	var input QueueItemInput
	if err := c.BodyParser(&input); err != nil {
		fmt.Println(err)
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
		Status:   "queued",
		Position: uint(queueLength + 1),
	}
	database.DB.Create(&queueItem)

	return c.Status(fiber.StatusCreated).JSON(queueItem)
}

func DeleteQueueItem(c *fiber.Ctx) error {

	queueItemId := c.AllParams()["id"]

	if queueItemId == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	// Get queue item from database
	queueItem := models.QueueItem{}
	if err := database.DB.Where("id = ?", queueItemId).First(&queueItem).Error; err != nil {
		return c.SendStatus(fiber.StatusNotFound)
	}

	// Delete queue item from database
	database.DB.Delete(&queueItem)

	return c.SendStatus(fiber.StatusOK)
}