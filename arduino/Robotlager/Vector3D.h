

struct Vector3D
{
    long int x, y, z;

    Vector3D(long int x, long int y, long int z)
    {
        this->x = x;
        this->y = y;
        this->z = z;
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
