#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "GazeProviderInterface.h"
#include "NullGazeProvider.generated.h"

UCLASS(BlueprintType)
class FPSGAZECORE_API UNullGazeProvider : public UObject, public IGazeProviderInterface
{
    GENERATED_BODY()

public:
    virtual FGazeSampleNormalized GetLatestSample_Implementation() const override;
    virtual bool IsAvailable_Implementation() const override;
    virtual EGazeProviderSource GetProviderSource_Implementation() const override;
};
