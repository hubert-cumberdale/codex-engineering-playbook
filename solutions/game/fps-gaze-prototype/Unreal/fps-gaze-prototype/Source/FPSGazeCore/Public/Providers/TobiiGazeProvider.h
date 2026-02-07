#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "GazeProviderInterface.h"
#include "TobiiGazeProvider.generated.h"

UCLASS(BlueprintType)
class FPSGAZECORE_API UTobiiGazeProvider : public UObject, public IGazeProviderInterface
{
    GENERATED_BODY()

public:
    virtual FGazeSampleNormalized GetLatestSample_Implementation() const override;
    virtual bool IsAvailable_Implementation() const override;
    virtual EGazeProviderSource GetProviderSource_Implementation() const override;

private:
    bool QueryTobiiRuntimeAvailability() const;
    FGazeSampleNormalized PullTobiiSample(double Timestamp) const;
};
