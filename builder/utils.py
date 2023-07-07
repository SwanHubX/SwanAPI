def check_elements_in_list(A, B):
    set_B = set(B)
    for element in A:
        if element not in set_B:
            return False
    return True
