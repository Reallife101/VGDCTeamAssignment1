import pandas as pd
import numpy as np

'''
Member CSV format:
Columns: 
1. Full Name
2. Full Discord Tag (***#1234)
3. Email
4. Premade Role
5. Are you already part of a pre-made pitched team?	
6. Which team are you part of as a pre-made member?
7. 1st choice
8. 2nd choice
9. 3rd choice	
10. Role [1st Choice]
11. Role [2nd Choice]
12. Role [3rd Choice]
13. Remaining Game choices
14. Role [Remaining]

Team Lead CSV format:
Columns: 
1. Full Discord Tag (***#1234)
2. Game
3. Position

Max Team CSV format:
Columns: 
1. Game
2. Role
3. Spots
'''

PRIMARY = "Primary role"
NO_PREFERENCE = "No Preference"
ANY_TEAM = "Put me on any team"
NO_OTHER_TEAMS = "If I do not receive my previous choice, do not assign me to a team."

# Score for [1st, 2nd, 3rd, 4th+, no team]
SCORE_MATRIX = [1, 3, 6, 20, 100]


def main(member_csv, teamlead_csv, max_team_count):
    team_assignments = []
    current_team_counts = {}
    current_spots_left = {}

    member_df = pd.read_csv(member_csv)
    teamlead_df = pd.read_csv(teamlead_csv)
    max_team_df = pd.read_csv(max_team_count)

    # Get any member list
    # get_all_any_teams(member_df)

    # Assign all premades
    for index, row in member_df.iterrows():

        # assign all pre-mades
        if not pd.isna(row.iloc[5]):
            team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[5], row.iloc[3], "Pre-made"])
            teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
            member_df = member_df.drop(index)

        # Otherwise Check for team lead requests
        else:
            for index2, row2 in teamlead_df.iterrows():
                # Check if discords are the same and their first pick is the same (including roles)
                if row2.iloc[0] == row.iloc[1] and row2.iloc[1] == row.iloc[6]:

                    # If the role wanted is in the row list, immediately add
                    if row2.iloc[2] in row.iloc[9]:
                        # Adds Name, Discord Tag, 1st Choice Game, Requested Role
                        team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[6], row2.iloc[2], "Requested"])
                        teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
                        member_df = member_df.drop(index)

                    # Roles don't match! Alert user!
                    else:
                        print(
                            f"{row.iloc[0]} wants a different role for {row.iloc[6]}! Requested to be {row[9]} but team lead wants {row2[2]}")

    # ----------- Input all spaces left for all games and positions -----------
    for index, row in max_team_df.iterrows():
        # The key is the game name, followed by a space, then the role
        key = f"{row.iloc[0]} {row.iloc[1]}"
        current_spots_left[key] = row.iloc[2]

    # ---For each game and role, get current total number of taken positions and remove them from current spots left----

    for team_mem in team_assignments:
        # If they are a premade, pass. They don't count towards totals
        if team_mem[4] == "Pre-made":
            continue

        # The key is the game name, followed by a space, then the role
        key = f"{team_mem[2]} {team_mem[3]}"

        # if not initialized, add it
        if key in current_spots_left:
            current_spots_left[key] -= 1

        else:
            current_spots_left[key] = -1
            print(f"Warning! {key} is missing from the max team sheet!")

    # --- Go through each row and assign people spots as long as theres space ---
    # Grade the assignment as well

    score = 0
    random_member_df = member_df.sample(frac=1)

    for index, row in random_member_df.iterrows():

        has_been_assigned = False

        # --------- Start with Choice #1 ---------
        # Split up base on possible roles
        for role in row.iloc[9].split(", "):
            # The key is the game name, followed by a space, then the role
            key = f"{row.iloc[6]} {role}"

            # if theres space, assign
            if current_spots_left[key] > 0:
                # Adds Name, Discord Tag, 1st Choice Game, Role
                team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[6], role, "Student First Choice"])
                teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])

                # decrease spots
                current_spots_left[key] -= 1

                # add score accordingly
                if "If I do not receive my previous choice, do not assign me to a team" in row.iloc[6]:
                    score += SCORE_MATRIX[4]
                else:
                    score += SCORE_MATRIX[0]

                has_been_assigned = True
                break

        # If has been assigned, go to next person
        if has_been_assigned:
            continue

        # --------- Choice #2 ---------
        # Split up base on possible roles
        for role in row.iloc[10].split(", "):
            # The key is the game name, followed by a space, then the role
            key = f"{row.iloc[7]} {role}"

            # if theres space, assign
            if current_spots_left[key] > 0:
                # Adds Name, Discord Tag, 1st Choice Game, Role
                team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[7], role, "Student Second Choice"])
                teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])

                # decrease spots
                current_spots_left[key] -= 1

                # add score accordingly
                if "If I do not receive my previous choice, do not assign me to a team" in row.iloc[7]:
                    score += SCORE_MATRIX[4]
                else:
                    score += SCORE_MATRIX[1]
                has_been_assigned = True
                break

        # If has been assigned, go to next person
        if has_been_assigned:
            continue

        # --------- Choice #3 ---------
        # Split up base on possible roles
        for role in row.iloc[11].split(", "):
            # The key is the game name, followed by a space, then the role
            key = f"{row.iloc[8]} {role}"

            # if theres space, assign
            if current_spots_left[key] > 0:
                # Adds Name, Discord Tag, 1st Choice Game, Role
                team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[8], role, "Student Third Choice"])
                teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])

                # decrease spots
                current_spots_left[key] -= 1

                # add score accordingly
                if "If I do not receive my previous choice, do not assign me to a team" in row.iloc[8]:
                    score += SCORE_MATRIX[4]
                else:
                    score += SCORE_MATRIX[2]
                has_been_assigned = True
                break

        # If has been assigned, go to next person
        if has_been_assigned:
            continue

        # --------- Choice #4+ ---------
        # Check if is nan
        if pd.isna(row.iloc[12]):
            # If is Nan, print error and move on
            print(f"Warning: {row.iloc[0]} did not get 1st, 2nd, or 3rd choice, and does not have 4+ choice")
            print(f"Games: {row.iloc[6]} {row.iloc[9]}, {row.iloc[7]} {row.iloc[10]}, {row.iloc[8]} {row.iloc[11]}")
            continue

        # Split up base on possible game
        for game in row.iloc[12].split(", "):
            # Split up base on possible roles
            for role in row.iloc[13].split(", "):
                # print(f"{row.iloc[0]}: {game} {role}")
                # The key is the game name, followed by a space, then the role
                key = f"{game} {role}"

                # if theres space, assign
                if current_spots_left[key] > 0:
                    # Adds Name, Discord Tag, 1st Choice Game, Role
                    team_assignments.append([row.iloc[0], row.iloc[1], game, role, "Student Fourth+ Choice"])
                    teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])

                    # decrease spots
                    current_spots_left[key] -= 1

                    # add score accordingly
                    if "If I do not receive my previous choice, do not assign me to a team" in game:
                        score += SCORE_MATRIX[4]
                    else:
                        score += SCORE_MATRIX[3]
                    has_been_assigned = True
                    break

            # If has been assigned, go to next person
            if has_been_assigned:
                break

        # If has been assigned, go to next person
        if has_been_assigned:
            continue

        # --- If we get here, they didn't get their first, second or third choice ---
        print(f"Warning: {row.iloc[0]} did not get 1st, 2nd, 3rd, or 4+ choice")
        print(f"Games: {row.iloc[6]} {row.iloc[9]}, {row.iloc[7]} {row.iloc[10]}, {row.iloc[8]} {row.iloc[11]},"
              f" {row.iloc[12]} {row.iloc[13]}")

    print(score)
    # for key in current_spots_left:
    #     print(f"{key}: {current_spots_left[key]}")

    # Save remaining team lead choices for inspection later
    teamlead_df.to_csv("leftover_team_choices.csv")

    # Convert to csv and sort
    nparray = np.array(team_assignments)
    pass1_csv = pd.DataFrame(nparray)
    pass1_csv = pass1_csv.set_axis(['Name', 'Discord', 'Game', 'Position', 'Reason'], axis=1)
    pass1_csv = pass1_csv.sort_values(['Game', 'Reason', 'Position', 'Name'])
    pass1_csv.to_csv(f"SingleExhaustive({score}).csv")


"""
    From previous Version

    # Assign everyone else their first choice
    for index, row in member_df.iterrows():
        # Adds Name, Discord Tag, 1st Choice Game, 1st Choice Role
        team_assignments.append([row.iloc[0], row.iloc[1], row.iloc[6], row.iloc[9], "Student First Choice"])
        teamlead_df = drop_from_csv(teamlead_df, row.iloc[1])
        pass
"""


def get_all_any_teams(member_df):
    '''
    writes a csv with all members who put down any team in any choice

    :param member_df: dataframe of members
    :return: nothing
    '''
    any_team_members = []

    # iterate through all members and make a list of all any teams
    for index, row in member_df.iterrows():
        if row.iloc[6] == ANY_TEAM:
            # Adds Name, Discord Tag, which choice is any choice
            any_team_members.append([row.iloc[0], row.iloc[1], "1st Choice Any Choice"])
        elif row.iloc[7] == ANY_TEAM:
            any_team_members.append([row.iloc[0], row.iloc[1], "2nd Choice Any Choice"])
        elif row.iloc[8] == ANY_TEAM:
            any_team_members.append([row.iloc[0], row.iloc[1], "3rd Choice Any Choice"])
        # Convert to csv and sort
    nparray = np.array(any_team_members)
    pass1_csv = pd.DataFrame(nparray)
    pass1_csv = pass1_csv.set_axis(['Name', 'Discord', 'Any team Choice'], axis=1)
    pass1_csv = pass1_csv.sort_values(['Any team Choice', 'Name'])
    pass1_csv.to_csv("AnyChoicePeople.csv")


def drop_from_csv(df, discord):
    '''
    drops a particular discord from a team lead dataframe

    :param df: team lead dataframe
    :param discord: discord of person to remove from team lead list
    :return: new dataframe without that person
    '''

    for index, row in df.iterrows():
        if row.iloc[0] == discord:
            df = df.drop(index)
    return df


if __name__ == '__main__':
    main('Spring 2024 Game Sign Up Form (Responses) - Sort Form Exhaustive.csv',
         'Spring 2024 Team Lead Mixer Sheet - Final Mixer Sheet.csv',
         "Spring 2024 Team Lead Mixer Sheet - Max Room Count.csv")
