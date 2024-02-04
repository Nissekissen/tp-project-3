package main

import (
	"robotlager/handlers"

	"github.com/gofiber/fiber/v2"
)

func setupRoutes(app *fiber.App) {
	app.Get("/queue", handlers.GetQueue)
	app.Post("/queue", handlers.AddItemToQueue)
	app.Get("/items", handlers.GetItems)
	app.Post("/items", handlers.CreateItem)
	app.Get("/items/:id", handlers.GetItem)
	app.Patch("/items/:id", handlers.UpdateItem)
}
