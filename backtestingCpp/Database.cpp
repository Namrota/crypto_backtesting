


#include "Database.h"
#include <chrono>
#include <cstdlib>

using namespace std;

Database::Database(const string& file_name)
{
    string FILE_NAME= "../../data/" + file_name + ".h5";

    hid_t fapl= H5Pcreate(H5P_FILE_ACCESS);

    herr_t status= H5Pset_libver_bounds(fapl, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);

    status= H5Pset_fclose_degree(fapl, H5F_CLOSE_STRONG);

    printf("Opening file: %s\n", FILE_NAME.c_str());
    h5_file = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);

    if(h5_file < 0) {
        FILE_NAME= "data/" + file_name + ".h5";
        h5_file = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);
        if(h5_file < 0) {
            fprintf(stderr, "Error opening file: %s\n", FILE_NAME.c_str());
        }
        
        
    }

}

void Database::close_file()
{
    if(h5_file >= 0) {
        herr_t status = H5Fclose(h5_file);
        if(status < 0) {
            fprintf(stderr, "Error closing file.\n");
        } else {
            printf("File closed successfully.\n");
        }
    } else {
        fprintf(stderr, "No file to close.\n");
    }
}

double **Database::get_data(const string &symbol, const string &exchange, int &array_size)
{
    double** results= {};

    hid_t dataset= H5Dopen2(h5_file, symbol.c_str(), H5P_DEFAULT);

    // Check if the dataset was opened successfully
    if(dataset == -1){
        fprintf(stderr, "Error opening dataset: %s\n", symbol.c_str());
        return results; // Return empty results if dataset cannot be opened
    }

    auto start_ts= chrono:: high_resolution_clock::now();

    // Acessing dataset's dataspace
    hid_t dspace= H5Dget_space(dataset);
    hsize_t dims[2];

    H5Sget_simple_extent_dims(dspace, dims, NULL);

    array_size = (int)dims[0]; // Set the array size to the number of rows in the dataset

    results= new double*[dims[0]];
    for(size_t i = 0; i < dims[0]; ++i) {
        results[i] = new double[dims[1]];
    }

    double* candles_arr = new double[dims[0] * dims[1]];
    H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, candles_arr);

    int j =  0;
    // Fill the results array with data from candles_arr
    for(int i = 0; i < (dims[0] * dims[1]); i+= 6) {
        results[j][0] = candles_arr[i];
        results[j][1] = candles_arr[i + 1];
        results[j][2] = candles_arr[i + 2];
        results[j][3] = candles_arr[i + 3];
        results[j][4] = candles_arr[i + 4];
        results[j][5] = candles_arr[i + 5];    
        j++;
    }

    // Clean up
    delete[] candles_arr;

    qsort(results, dims[0], sizeof(results[0]), compare);

    // Close the dataspace and dataset
    H5Sclose(dspace);
    H5Dclose(dataset);

    
    auto end_ts= chrono:: high_resolution_clock::now();
    // Calculate and print the time taken to read the dataset
    auto duration= chrono:: duration_cast<chrono:: milliseconds>(end_ts - start_ts);
    printf("Time taken to read %i data for exchange %s and symbol %s: %i ms\n", (int)dims[0],
           exchange.c_str(), symbol.c_str(), (int)duration.count());
    return results; // Return the filled results array
}

int compare(const void *a, const void *b)
{
    const double* row_a = *(double**)a;
    const double* row_b = *(double**)b;

    // Compare the first column (timestamp)
    if(row_a[0] < row_b[0]) return -1;
    if(row_a[0] > row_b[0]) return 1;
    return 0; // Rows are equal
}