#pragma once

#include "CoreMinimal.h"
#include "UObject/Interface.h"
#include "GazeSignalTypes.h"
#include "GazeProviderInterface.generated.h"

UINTERFACE(BlueprintType)
class UGazeProviderInterface : public UInterface
{
    GENERATED_BODY()
};

class FPSGAZECORE_API IGazeProviderInterface
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "Gaze|Provider")
    FGazeSampleNormalized GetLatestSample() const;

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "Gaze|Provider")
    bool IsAvailable() const;

    UFUNCTION(BlueprintCallable, BlueprintNativeEvent, Category = "Gaze|Provider")
    EGazeProviderSource GetProviderSource() const;
};
