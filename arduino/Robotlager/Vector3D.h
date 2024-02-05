#ifndef VECTOR_H
#define VECTOR_H

struct Temp {
  int x;
  int y;
  int z;

  Temp() {};
};

Temp parseRawData(uint8_t data)
{
    uint8_t xRaw = (data >> 4) & 0x03; // 110000
    uint8_t yRaw = (data >> 2) & 0x03; // 001100
    uint8_t zRaw = data & 0x03;        // 000011

    Temp parsedData;

    // TODO: change these to actual percentages for the box positions.
    parsedData.x = map(xRaw, 0, 3, 0, 100);
    parsedData.y = map(yRaw, 0, 3, 0, 100);

    // Z

    switch (zRaw)
    {
    case 0:
        parsedData.z = 25;
        break;
    case 1:
        parsedData.z = 50;
        break;
    case 2:
        parsedData.z = 75;
        break;
    case 3:
        parsedData.z = 100;
        break;
    default:
        parsedData.z = 0;
        break;
    }

    return parsedData;
}

struct Vector3D
{
    long int x, y, z;

    Vector3D(long int x, long int y, long int z)
    {
        this->x = x;
        this->y = y;
        this->z = z;
    }

    Vector3D(uint8_t dataChar) {
        Temp data = parseRawData(dataChar);
        x = data.x;
        y = data.y;
        z = data.z;
    }

    Vector3D()
    {
        this->x = 0;
        this->y = 0;
        this->z = 0;
    }

    Vector3D operator+(const Vector3D &other)
    {
        return Vector3D(this->x + other.x, this->y + other.y, this->z + other.z);
    }

    Vector3D operator-(const Vector3D &other)
    {
        return Vector3D(this->x - other.x, this->y - other.y, this->z - other.z);
    }
};

#endif