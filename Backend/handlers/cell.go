package handlers

import (
	"fmt"
	"robotlager/database"
	"robotlager/models"

	"github.com/gofiber/fiber/v2"
)

func GetCell(c *fiber.Ctx) error {

	id := c.AllParams()["id"]
	if id == "" {
		return c.SendStatus(fiber.StatusBadRequest)
	}

	cell := models.Cell{}
	query := database.DB.Where("id = ?", id).First(&cell)
	if query.Error != nil {
		return c.SendStatus(fiber.StatusNotFound)
	}

	return c.JSON(cell)
}

func GetCells(c *fiber.Ctx) error {

	cells := []models.Cell{}
	query := database.DB.Find(&cells)
	if query.Error != nil {
		return c.Status(500).SendString("Could not get cells")
	}

	return c.JSON(cells)
}

func CreateCell(c *fiber.Ctx) error {

	type CellInput struct {
		X uint `json:"x"`
		Y uint `json:"y"`
		Z uint `json:"z"`
	}

	var input CellInput
	if err := c.BodyParser(&input); err != nil {
		fmt.Println(err)
		return c.Status(400).SendString("Could not parse JSON")
	}

	// Create new cell
	cell := models.Cell{
		X: input.X,
		Y: input.Y,
		Z: input.Z,
	}
	database.DB.Create(&cell)

	return c.Status(fiber.StatusCreated).JSON(cell)
}