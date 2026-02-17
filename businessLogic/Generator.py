from itertools import combinations
from . import MatchDto
from . import Team

class Generator:
    @staticmethod
    def GenerateMatchesAmericano(players, maxTours):
        pairs = list(combinations(players, 2))
        matches = []
        for i in range(len(pairs)):
            pairA = pairs[i]
            teamA = { pairA[0], pairA[1] }
            teamALevel = pairA[0].sportLevel + pairA[1].sportLevel
            for j in range(i + 1, len(pairs)):
                pairB = pairs[j]
                teamB = { pairB[0], pairB[1] }
                teamBLevel = pairB[0].sportLevel + pairB[1].sportLevel
                if teamA.isdisjoint(teamB):
                    levelDiff = abs(teamBLevel - teamALevel)
                    match = MatchDto.MatchDto(Team.Team(pairA[0], pairA[1]), Team.Team(pairB[0], pairB[1]), levelDiff)
                    matches.append((levelDiff, match))
        matches.sort(key = lambda t: t[0])
        result = []
        for _, m in matches:
            result.append(m)
        return result

