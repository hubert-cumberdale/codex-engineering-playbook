#include "Providers/TobiiGazeProvider.h"

#include "HAL/PlatformTime.h"

#if WITH_TOBII_EYETRACKING
// The Tobii SDK/plugin include must stay scoped to this provider implementation.
#include "ITobiiCore.h"
#endif

FGazeSampleNormalized UTobiiGazeProvider::GetLatestSample_Implementation() const
{
    const double Timestamp = FPlatformTime::Seconds();
    if (!QueryTobiiRuntimeAvailability())
    {
        return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Tobii, Timestamp);
    }

    return PullTobiiSample(Timestamp);
}

bool UTobiiGazeProvider::IsAvailable_Implementation() const
{
    return QueryTobiiRuntimeAvailability();
}

EGazeProviderSource UTobiiGazeProvider::GetProviderSource_Implementation() const
{
    return EGazeProviderSource::Tobii;
}

bool UTobiiGazeProvider::QueryTobiiRuntimeAvailability() const
{
#if WITH_TOBII_EYETRACKING
    return true;
#else
    return false;
#endif
}

FGazeSampleNormalized UTobiiGazeProvider::PullTobiiSample(double Timestamp) const
{
#if WITH_TOBII_EYETRACKING
    FGazeSampleNormalized Sample;
    Sample.gaze_x = 0.5f;
    Sample.gaze_y = 0.5f;
    Sample.confidence = 1.0f;
    Sample.present = true;
    Sample.source = EGazeProviderSource::Tobii;
    Sample.timestamp = Timestamp;
    return Sample;
#else
    return FGazeSampleNormalized::MakeNoGaze(EGazeProviderSource::Tobii, Timestamp);
#endif
}
