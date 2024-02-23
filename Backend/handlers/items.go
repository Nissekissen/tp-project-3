package handlers

import (
	"fmt"
	"robotlager/database"
	"robotlager/models"

	"github.com/gofiber/fiber/v2"
)

func GetItems(c *fiber.Ctx) error {

	// Get all items from database
	items := []models.Item{}
	query := database.DB.Model(&models.Item{}).Find(&items)
	if query.Error != nil {
		return c.Status(500).SendString("Could not get items")
	}

	return c.JSON(items)
}

func GetItem(c *fiber.Ctx) error {

	itemId := c.AllParams()["id"]
	if itemId == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	// Get item from database
	item := models.Item{}
	// query := database.DB.Model(&models.Item{}).Where("id = ?", c.Params("id")).First(&item)
	if err := database.DB.Where("id = ?", itemId).First(&item).Error; err != nil {
		return c.SendStatus(fiber.StatusNotFound)
	}

	return c.JSON(item)
}

func CreateItem(c *fiber.Ctx) error {

	type ItemInput struct {
		Name        string `json:"name"`
		StartAmount int `json:"start_amount"`
	}

	
	var input ItemInput
	if err := c.BodyParser(&input); err != nil {
		fmt.Println(err)
		return c.Status(400).SendString("Could not parse JSON")
	}

	fmt.Println(input.Name)

	// Create new item
	item := models.Item{
		Name:   input.Name,
		Amount: uint(input.StartAmount),
	}
	database.DB.Create(&item)

	// Add a queue item to the queue with the type CREATED
	queueItem := models.QueueItem{
		ItemID:   item.ID,
		Amount:   int(item.Amount),
		Status:   int(models.QUEUED),
		Type:     int(models.CREATED),
	}
	database.DB.Create(&queueItem)

	return c.Status(fiber.StatusCreated).JSON(item)
}

func DeleteItem(c *fiber.Ctx) error {
	
	itemId := c.AllParams()["id"]
	if itemId == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	// Delete item from database
	database.DB.Where("id = ?", itemId).Delete(&models.Item{})

	// Delete all queue items with the same itemID
	database.DB.Where("item_id = ?", itemId).Delete(&models.QueueItem{})

	return c.SendStatus(fiber.StatusOK)
}

func UpdateItem(c *fiber.Ctx) error {

	itemId := c.AllParams()["id"]
	if itemId == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	type ItemInput struct {
		Name        string `json:"name"`
		CellID      uint `json:"cell_id"`
		Amount int `json:"start_amount"`
	}

	var input ItemInput
	if err := c.BodyParser(&input); err != nil {
		return c.Status(400).SendString("Could not parse JSON")
	}

	// Create new item
	item := models.Item{
		Name:   input.Name,
		Amount: uint(input.Amount),
		CellID: input.CellID,
	}

	// Update item
	database.DB.Model(&models.Item{}).Where("id = ?", itemId).Updates(&item)

	return c.Status(fiber.StatusOK).JSON(item)
}
