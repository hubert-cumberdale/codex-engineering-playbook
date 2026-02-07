#include "GazeProviderSettings.h"

UGazeProviderSettings::UGazeProviderSettings()
{
    bGazeEnabled = true;
    GazeProvider = TEXT("Null");
    ConfidenceThreshold = 0.60f;
}
