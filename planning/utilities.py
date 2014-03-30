from math import tan, pi, hypot, log

DISTANCE_MATCH_THRESHOLD = 15
ANGLE_MATCH_THRESHOLD = pi/10
BALL_ANGLE_THRESHOLD = pi/20
MAX_DISPLACEMENT_SPEED = 690
MAX_ANGLE_SPEED = 50


def is_shot_blocked(world, our_robot, their_robot):
    '''
    Checks if our robot could shoot past their robot
    '''
    predicted_y = predict_y_intersection(
        world, their_robot.x, our_robot, full_width=True, bounce=True)
    if predicted_y is None:
        return True
    return abs(predicted_y - their_robot.y) < their_robot.length + 40


def is_attacker_shot_blocked(world, our_attacker, their_defender):
    '''
    Checks if our attacker would score if it would immediately turn and shoot.
    '''

    # Acceptable distance that the opponent defender can be relative to our
    # shooting position in order for us to have a clear shot.
    distance_threshold = 50
    return abs(our_attacker.y - their_defender.y) > distance_threshold


def predict_y_intersection(world, predict_for_x, robot, full_width=False, bounce=False):
        '''
        Predicts the (x, y) coordinates of the ball shot by the robot
        Corrects them if it's out of the bottom_y - top_y range.
        If bounce is set to True, predicts for a bounced shot
        Returns None if the robot is facing the wrong direction.
        '''
        x = robot.x
        y = robot.y
        top_y = world._pitch.height if full_width else world.our_goal.y + (world.our_goal.width/2) - 30
        bottom_y = 0 if full_width else world.our_goal.y - (world.our_goal.width/2) + 30
        angle = robot.angle
        if (robot.x < predict_for_x and not (pi/2 < angle < 3*pi/2)) or (robot.x > predict_for_x and (3*pi/2 > angle > pi/2)):
            if bounce:
                if not (0 <= (y + tan(angle) * (predict_for_x - x)) <= world._pitch.height):
                    bounce_pos = 'top' if (y + tan(angle) * (predict_for_x - x)) > world._pitch.height else 'bottom'
                    x += (world._pitch.height - y) / tan(angle) if bounce_pos == 'top' else (0 - y) / tan(angle)
                    y = world._pitch.height if bounce_pos == 'top' else 0
                    angle = (-angle) % (2*pi)
            predicted_y = (y + tan(angle) * (predict_for_x - x))
            # Correcting the y coordinate to the closest y coordinate on the goal line:
            if predicted_y > top_y:
                return top_y
            elif predicted_y < bottom_y:
                return bottom_y
            return predicted_y
        else:
            return None


def grab_ball():
    return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 1, 'speed': 1000}


def kick_ball():
    return {'left_motor': 0, 'right_motor': 0, 'kicker': 1, 'catcher': 0, 'speed': 1000}


def open_catcher():
    return {'left_motor': 0, 'right_motor': 0, 'kicker': 1, 'catcher': 0, 'speed': 1000}


def has_matched(robot, x=None, y=None, angle=None,
                angle_threshold=ANGLE_MATCH_THRESHOLD, distance_threshold=DISTANCE_MATCH_THRESHOLD):
    dist_matched = True
    angle_matched = True
    if not(x is None and y is None):
        dist_matched = hypot(robot.x - x, robot.y - y) < distance_threshold
    if not(angle is None):
        angle_matched = abs(angle) < angle_threshold
    return dist_matched and angle_matched



def calculate_motor_speed(displacement, angle, backwards_ok=False, careful=False):
    '''
    Simplistic view of calculating the speed: no modes or trying to be careful
    '''
    moving_backwards = False
    general_speed = 95 if careful else 300
    angle_thresh = BALL_ANGLE_THRESHOLD if careful else ANGLE_MATCH_THRESHOLD

    if backwards_ok and abs(angle) > pi/2:
        angle = (-pi + angle) if angle > 0 else (pi + angle)
        moving_backwards = True

    if not (displacement is None):

        if displacement < DISTANCE_MATCH_THRESHOLD:
            return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        elif abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        else:
            speed = log(displacement, 10) * MAX_DISPLACEMENT_SPEED
            speed = -speed if moving_backwards else speed
            return {'left_motor': speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': 1000/(1+10**(-0.1*(displacement-100)))}

    else:

        if abs(angle) > angle_thresh:
            speed = (angle/pi) * MAX_ANGLE_SPEED
            return {'left_motor': -speed, 'right_motor': speed, 'kicker': 0, 'catcher': 0, 'speed': general_speed}

        else:
            return {'left_motor': 0, 'right_motor': 0, 'kicker': 0, 'catcher': 0, 'speed': general_speed}



def do_nothing():
    return calculate_motor_speed(0, 0)
