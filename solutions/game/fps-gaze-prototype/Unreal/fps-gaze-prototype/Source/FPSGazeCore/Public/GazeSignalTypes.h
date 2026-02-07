#pragma once

#include "CoreMinimal.h"
#include "GazeSignalTypes.generated.h"

UENUM(BlueprintType)
enum class EGazeProviderSource : uint8
{
    Null = 0,
    Tobii = 1,
};

USTRUCT(BlueprintType)
struct FGazeSampleNormalized
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    float gaze_x = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    float gaze_y = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    float confidence = 0.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    bool present = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    EGazeProviderSource source = EGazeProviderSource::Null;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gaze")
    double timestamp = 0.0;

    static FGazeSampleNormalized MakeNoGaze(EGazeProviderSource InSource, double InTimestamp)
    {
        FGazeSampleNormalized Sample;
        Sample.gaze_x = 0.0f;
        Sample.gaze_y = 0.0f;
        Sample.confidence = 0.0f;
        Sample.present = false;
        Sample.source = InSource;
        Sample.timestamp = InTimestamp;
        return Sample;
    }
};
