#include <iostream>
#include "Database.h"
#include "utils.h"

int main(int, char**){
    Database db("binance"); 
    int array_size = 0;
    double **res= db.get_data("BTCUSDT", "binance", array_size);
    std::vector<double> ts, open, high, low, close, volume;
    std::tie(ts, open, high, low, close, volume)= rearrange_candles(res, "15m", array_size); // Example usage of rearrange_candles
    for(int i = 0; i < 50; i++) {
        printf("Timestamp: %f, Open: %f, High: %f, Low: %f, Close: %f, Volume: %f\n", 
               ts[i], open[i], high[i], low[i], close[i], volume[i]);
    }
    printf("%i\n", ts.size());        
    
    db.close_file();
    
   
}
