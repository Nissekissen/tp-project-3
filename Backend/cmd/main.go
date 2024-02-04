package main

import (
	"fmt"
	"robotlager/database"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
)

func main() {
	database.Connect()
	app := fiber.New()

	app.Use(cors.New())

	setupRoutes(app)
	app.Listen(":3000")
	fmt.Println("Server is running on port 3000")
}
