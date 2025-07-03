#include <string>
#include <tuple>
#include <vector>

std:: tuple<std::vector<double>, std::vector<double>, std::vector<double>, std::vector<double>,
std::vector<double>, std::vector<double>> rearrange_candles(double** candles, std:: string tf, int array_size);