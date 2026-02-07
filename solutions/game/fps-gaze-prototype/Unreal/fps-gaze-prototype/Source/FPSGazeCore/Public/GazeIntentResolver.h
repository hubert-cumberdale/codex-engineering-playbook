#pragma once

#include "CoreMinimal.h"
#include "GazeIntentTypes.h"
#include "GazeSignalTypes.h"

class FPSGAZECORE_API FGazeIntentResolver
{
public:
    static FGazeIntentOutput Resolve(
        const FGazeSampleNormalized& Sample,
        const FGazeIntentResolverSettings& Settings,
        const FGazeIntentSceneModel& SceneModel
    );

private:
    static bool IsSuppressed(const FGazeSampleNormalized& Sample, const FGazeIntentResolverSettings& Settings);
};
