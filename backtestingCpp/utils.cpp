

#include <math.h>
#include "utils.h"
using namespace std;

tuple<vector<double>, vector<double>, vector<double>, vector<double>,
vector<double>, vector<double>> rearrange_candles(double** candles, std:: string tf, 
    long long from_time, long long to_time, int array_size)
{
    vector<double> ts, open, high, low, close, volume;
    
    double tf_result;
    //Check if the string contains the letter 'm' for minutes, 'h' for hours, or 'd' for days
    if(tf.find("m") != string::npos) {
        string minutes = tf.substr(0, tf.find("m")); 
        // Convert minutes to milliseconds
        tf_result = stod(minutes) * 60 * 1000; 
    } else if(tf.find("h") != string::npos) {
        tf_result = stod(tf.substr(0, tf.find("h"))) * 60 * 60 * 1000; // Convert hours to milliseconds
    } else if(tf.find("d") != string::npos) {
        tf_result = stod(tf.substr(0, tf.find("d"))) * 24 * 60 * 60 * 1000; // Convert days to milliseconds
    } else {
        printf("Unsupported time frame format for %s\n", tf.c_str());
        return make_tuple(ts, open, high, low, close, volume);
    }

    double current_ts= 0.0; 
    double current_open;
    double current_high;
    double current_low;
    double current_close;
    double current_volume;

    // Loop through the candles array and fill the vectors
    for(int i = 0; i < array_size; i++) {


        if(candles[i][0] < from_time){
            continue; 
        }
        else if(current_ts == 0.0) {
            current_ts= candles[i][0] - fmod(candles[0][0], tf_result); // Convert the first timestamp to milliseconds
            current_open = candles[i][1];
            current_high = candles[i][2];
            current_low = candles[i][3];
            current_close = candles[i][4];
            current_volume = candles[i][5];
            
        }
        if(candles[i][0] > to_time){
            break; // Stop processing if the candle timestamp exceeds the to_time
        }

        

        if(candles[i][0] >= current_ts + tf_result) {
            // If the current timestamp exceeds the current timestamp plus the time frame, save the current candle
            ts.push_back(current_ts);
            open.push_back(current_open);
            high.push_back(current_high);
            low.push_back(current_low);
            close.push_back(current_close);
            volume.push_back(current_volume);
            
            int missing_candles= (candles[i][0] - current_ts) / tf_result - 1;
            // If there are missing candles, fill them with the current candle values
            if(missing_candles > 0) {
                printf("Missing %d candles between %f and %f\n", missing_candles, current_ts, candles[i][0]);
                for(int j = 0; j < missing_candles; j++) {
                    ts.push_back(current_ts + (j + 1) * tf_result);
                    // Fill in the  missing candles with the last close price
                    // we assume the open, high, low, and close are the same as the last known candle
                    open.push_back(current_close);
                    high.push_back(current_close);
                    low.push_back(current_close);
                    close.push_back(current_close);
                    volume.push_back(0); // Volume is set to 0 for missing candles
                }
            }
            // Reset the current candle values to the new candle
            current_ts = candles[i][0]-fmod(candles[i][0], tf_result); // Update the current timestamp
            current_open = candles[i][1]; // Update the current open
            current_high = candles[i][2]; // Update the current high
            current_low = candles[i][3]; // Update the current low
            current_close = candles[i][4]; // Update the current close
            current_volume = candles[i][5]; // Update the current volume
        }
       else{
            if(candles[i][2] > current_high) {
                current_high = candles[i][2]; // Update the current high
            }
            if(candles[i][3] < current_low || current_low == 0) {
                current_low = candles[i][3]; // Update the current low
            }
            current_close = candles[i][4]; // Update the current close
            current_volume += candles[i][5]; // Update the current volume

       }
    }
    return make_tuple(ts, open, high, low, close, volume);

}