package handlers

import (
	"fmt"
	"robotlager/database"
	"robotlager/models"
	"strconv"

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
		CellID      string `json:"cell_id"`
		StartAmount string `json:"start_amount"`
	}

	var input ItemInput
	if err := c.BodyParser(&input); err != nil {
		return c.Status(400).SendString("Could not parse JSON")
	}

	startAmountINT, err := strconv.Atoi(input.StartAmount)
	if err != nil {
		return c.Status(400).SendString("Could not parse start amount")
	}

	cellIDINT, err := strconv.Atoi(input.CellID)
	if err != nil {
		return c.Status(400).SendString("Could not parse cell ID")
	}

	// Create new item
	item := models.Item{
		Name:   input.Name,
		Amount: uint(startAmountINT),
		CellID: uint(cellIDINT),
	}
	fmt.Println(item)
	database.DB.Create(&item)

	return c.Status(fiber.StatusCreated).JSON(item)
}

func UpdateItem(c *fiber.Ctx) error {

	itemId := c.AllParams()["id"]
	if itemId == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	type ItemInput struct {
		Name        string `json:"name"`
		CellID      string `json:"cell_id"`
		StartAmount string `json:"start_amount"`
	}

	var input ItemInput
	if err := c.BodyParser(&input); err != nil {
		return c.Status(400).SendString("Could not parse JSON")
	}

	fmt.Println(c.Body())

	startAmountINT, err := strconv.Atoi(input.StartAmount)
	if err != nil {
		fmt.Println(err)
		return c.Status(400).SendString("Could not parse start amount")
	}

	cellIDINT, err := strconv.Atoi(input.CellID)
	if err != nil {
		return c.Status(400).SendString("Could not parse cell ID")
	}

	// Create new item
	item := models.Item{
		Name:   input.Name,
		Amount: uint(startAmountINT),
		CellID: uint(cellIDINT),
	}

	// Update item
	database.DB.Model(&models.Item{}).Where("id = ?", itemId).Updates(&item)

	return c.Status(fiber.StatusCreated).JSON(item)
}
