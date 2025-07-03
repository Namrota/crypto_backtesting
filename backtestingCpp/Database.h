/*
This is a header file for a Database class that manages an HDF5 file.
It includes necessary headers and defines the class with a constructor 
and a method to close the file.
*/

#include <string>
#include <hdf5.h>
class Database
{
    public:
        Database(const std::string &filename);
        void close_file();
        //two dimensional array size [n][m] 
        //where n is the number of rows and m is the number of columns
        // returns a pointer to a two-dimensional array of doubles
        double** get_data(const std::string &symbol, const std:: string &exchange, int &array_size);
        hid_t h5_file;
};

int compare(const void *a, const void *b);