from functools import reduce 
from operator import mul

def get_suit(card):
  """
  This function returns the suit of the given card.
  """
  
  return card[1]

def getValue(trick):
  values = {"J":3, "9":2, "T":1, "1":1, "K":0, "Q":0, "8":0, "7":0}
  total = 0
  for card in trick:
    total += values[card[0]]
  return total


def get_suit_card(cards, card_suit):
  """
  This function returns the list of cards of the given suit from the initial list of cards.
  """
  
  return [i for i in cards if get_suit(i) == card_suit]

def reshape(lst, shape):
    if len(shape) == 1:
        return lst
    n = reduce(mul, shape[1:])
    return [reshape(lst[i*n:(i+1)*n], shape[1:]) for i in range(len(lst)//n)]
  
