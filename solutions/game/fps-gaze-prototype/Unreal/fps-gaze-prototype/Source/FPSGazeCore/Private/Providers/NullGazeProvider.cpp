#include "Providers/NullGazeProvider.h"

#include "HAL/PlatformTime.h"

FGazeSampleNormalized UNullGazeProvider::GetLatestSample_Implementation() const
{
    return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Null, FPlatformTime::Seconds());
}

bool UNullGazeProvider::IsAvailable_Implementation() const
{
    return true;
}

EGazeProviderSource UNullGazeProvider::GetProviderSource_Implementation() const
{
    return EGazeProviderSource::Null;
}
